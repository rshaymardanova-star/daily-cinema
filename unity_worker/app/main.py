import io
import json
import logging
import subprocess
import tempfile
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage as gcs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    gcs_endpoint: str = "http://gcs:4443"
    gcs_bucket: str = "dailycinema"

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(title="Daily Cinema Unity Worker", version="0.1.0")

jobs: dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=2)


class RenderRequest(BaseModel):
    job_id: str
    project_id: str
    scene: dict


class RenderStatus(BaseModel):
    job_id: str
    status: str
    video_url: str = ""


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
                logger.info("Downloaded frame: %s", frame_path)
            except Exception as e:
                logger.error("Failed to download frame from %s: %s", url, e)
    return frames


def render_video(frames: list[str], work_dir: str) -> str:
    output_path = os.path.join(work_dir, "final.mp4")

    if not frames:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i",
                "color=c=black:s=1280x720:d=3",
                "-vf", "drawtext=text='Daily Cinema - No Frames':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
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
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", "24",
            output_path,
        ],
        check=True, capture_output=True,
    )
    return output_path


def run_render(job_id: str, project_id: str, scene: dict):
    try:
        logger.info("Starting render for job %s", job_id)
        with tempfile.TemporaryDirectory() as work_dir:
            frames = download_frames(scene, work_dir)
            logger.info("Downloaded %d frames", len(frames))

            video_path = render_video(frames, work_dir)
            logger.info("Rendered video: %s", video_path)

            client = get_gcs_client()
            bucket = ensure_bucket(client, settings.gcs_bucket)

            blob_path = f"projects/{project_id}/render/final.mp4"
            blob = bucket.blob(blob_path)
            blob.upload_from_filename(video_path, content_type="video/mp4")

            video_url = f"{settings.gcs_endpoint}/storage/v1/b/{settings.gcs_bucket}/o/{blob_path}?alt=media"

            jobs[job_id] = {
                "job_id": job_id,
                "status": "completed",
                "video_url": video_url,
            }
            logger.info("Render job %s completed", job_id)

    except Exception as e:
        logger.exception("Render job %s failed: %s", job_id, e)
        jobs[job_id] = {
            "job_id": job_id,
            "status": "failed",
            "video_url": "",
        }


@app.post("/render", response_model=RenderStatus)
async def render(req: RenderRequest):
    jobs[req.job_id] = {
        "job_id": req.job_id,
        "status": "processing",
        "video_url": "",
    }
    executor.submit(run_render, req.job_id, req.project_id, req.scene)
    return RenderStatus(**jobs[req.job_id])


@app.get("/status/{job_id}", response_model=RenderStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        return RenderStatus(job_id=job_id, status="not_found")
    return RenderStatus(**jobs[job_id])


@app.get("/health")
async def health():
    return {"status": "ok"}
