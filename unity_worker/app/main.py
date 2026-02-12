import logging
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage as gcs
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
    rename_fields={"asctime": "timestamp", "levelname": "level"},
))
root_logger = logging.getLogger()
root_logger.handlers.clear()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)

RENDER_DURATION = Histogram("unity_render_duration_seconds", "Render duration", ["template", "status"])
RENDER_TOTAL = Counter("unity_render_total", "Total renders", ["template", "status"])
JOBS_IN_PROGRESS = Gauge("unity_jobs_in_progress", "Render jobs in progress")
FRAMES_DOWNLOADED = Counter("unity_frames_downloaded_total", "Total frames downloaded")

TEMPLATES = {
    "default": {"description": "Standard 24fps H.264", "fps": 24, "preset": "medium", "crf": 23},
    "cinematic": {"description": "Cinematic 30fps high quality", "fps": 30, "preset": "slow", "crf": 18},
    "fast_preview": {"description": "Fast preview 15fps", "fps": 15, "preset": "ultrafast", "crf": 28},
}
DEFAULT_TEMPLATE = "default"

material_cache: dict[str, bool] = {}


class Settings(BaseSettings):
    gcs_endpoint: str = "http://gcs:4443"
    gcs_bucket: str = "dailycinema"
    redis_url: str = "redis://redis:6379/0"
    max_workers: int = 2
    ffmpeg_threads: int = 4

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(title="Daily Cinema Unity Worker", version="1.0.0")
Instrumentator(excluded_handlers=["/health/live", "/health/ready", "/metrics"]).instrument(app).expose(app)

jobs: dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=settings.max_workers)


class RenderRequest(BaseModel):
    job_id: str
    project_id: str
    scene: dict
    template: str = "default"


class RenderStatus(BaseModel):
    job_id: str
    status: str
    video_url: str = ""
    template: str = ""
    duration_ms: float = 0


def get_gcs_client() -> gcs.Client:
    client = gcs.Client(
        project="dailycinema",
        credentials=AnonymousCredentials(),
    )
    client._connection.API_BASE_URL = settings.gcs_endpoint
    return client


def ensure_bucket(client: gcs.Client, bucket_name: str) -> gcs.Bucket:
    bucket = client.bucket(bucket_name)
    try:
        if not bucket.exists():
            bucket = client.create_bucket(bucket_name)
    except Exception:
        try:
            bucket = client.create_bucket(bucket_name)
        except Exception:
            pass
    return bucket


def download_frames(scene: dict, work_dir: str) -> list[str]:
    frames = []
    for shot in scene.get("shots", []):
        for i, url in enumerate(shot.get("frame_urls", [])):
            try:
                resp = httpx.get(url, verify=False, timeout=30.0)
                resp.raise_for_status()
                frame_path = os.path.join(work_dir, f"shot_{shot['shot_id']}_frame_{i:03d}.png")
                with open(frame_path, "wb") as f:
                    f.write(resp.content)
                frames.append(frame_path)
                FRAMES_DOWNLOADED.inc()
                logger.info("Downloaded frame: %s", frame_path)
            except Exception as e:
                logger.error("Failed to download frame from %s: %s", url, e)
    return frames


def render_video(frames: list[str], work_dir: str, template_name: str = DEFAULT_TEMPLATE) -> str:
    template = TEMPLATES.get(template_name, TEMPLATES[DEFAULT_TEMPLATE])
    output_path = os.path.join(work_dir, "final.mp4")

    if not frames:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i",
                "color=c=black:s=1920x1080:d=3",
                "-vf", "drawtext=text='Daily Cinema - No Frames':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-threads", str(settings.ffmpeg_threads),
                output_path,
            ],
            check=True, capture_output=True,
        )
        return output_path

    concat_file = os.path.join(work_dir, "concat.txt")
    with open(concat_file, "w") as f:
        for frame in frames:
            f.write(f"file '{frame}'\n")
            f.write("duration 2\n")
        f.write(f"file '{frames[-1]}'\n")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_file,
            "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264",
            "-preset", template["preset"],
            "-crf", str(template["crf"]),
            "-pix_fmt", "yuv420p",
            "-r", str(template["fps"]),
            "-threads", str(settings.ffmpeg_threads),
            "-movflags", "+faststart",
            output_path,
        ],
        check=True, capture_output=True,
    )
    return output_path


def run_render(job_id: str, project_id: str, scene: dict, template_name: str):
    start = time.monotonic()
    JOBS_IN_PROGRESS.inc()
    try:
        logger.info("Starting render for job %s with template %s", job_id, template_name)
        with tempfile.TemporaryDirectory() as work_dir:
            frames = download_frames(scene, work_dir)
            logger.info("Downloaded %d frames", len(frames))

            video_path = render_video(frames, work_dir, template_name)
            logger.info("Rendered video: %s", video_path)

            client = get_gcs_client()
            bucket = ensure_bucket(client, settings.gcs_bucket)

            blob_path = f"projects/{project_id}/render/final.mp4"
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(video_path, content_type="video/mp4")

            video_url = f"{settings.gcs_endpoint}/storage/v1/b/{settings.gcs_bucket}/o/{blob_path}?alt=media"
            duration = (time.monotonic() - start) * 1000

            jobs[job_id] = {
                "job_id": job_id,
                "status": "completed",
                "video_url": video_url,
                "template": template_name,
                "duration_ms": duration,
            }
            RENDER_DURATION.labels(template=template_name, status="completed").observe(time.monotonic() - start)
            RENDER_TOTAL.labels(template=template_name, status="completed").inc()
            logger.info("Render job %s completed in %.0fms", job_id, duration)

    except Exception as e:
        logger.exception("Render job %s failed: %s", job_id, e)
        RENDER_DURATION.labels(template=template_name, status="failed").observe(time.monotonic() - start)
        RENDER_TOTAL.labels(template=template_name, status="failed").inc()
        jobs[job_id] = {
            "job_id": job_id,
            "status": "failed",
            "video_url": "",
            "template": template_name,
            "duration_ms": 0,
        }
    finally:
        JOBS_IN_PROGRESS.dec()


@app.post("/render", response_model=RenderStatus)
async def render(req: RenderRequest):
    template = req.template if req.template in TEMPLATES else DEFAULT_TEMPLATE
    jobs[req.job_id] = {
        "job_id": req.job_id,
        "status": "processing",
        "video_url": "",
        "template": template,
        "duration_ms": 0,
    }
    executor.submit(run_render, req.job_id, req.project_id, req.scene, template)
    return RenderStatus(**jobs[req.job_id])


@app.get("/status/{job_id}", response_model=RenderStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        return RenderStatus(job_id=job_id, status="not_found")
    return RenderStatus(**jobs[job_id])


@app.get("/templates")
async def list_templates():
    return {"templates": {k: v["description"] for k, v in TEMPLATES.items()}, "default": DEFAULT_TEMPLATE}


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        ffmpeg_ok = result.returncode == 0
    except Exception:
        ffmpeg_ok = False
    return {"status": "ready" if ffmpeg_ok else "degraded", "ffmpeg": "ok" if ffmpeg_ok else "missing", "workers": settings.max_workers}


@app.get("/health")
async def health():
    return {"status": "ok"}
