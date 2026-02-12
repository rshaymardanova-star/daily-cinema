import io
import logging
import sys
import time
import random
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from PIL import Image, ImageDraw
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

GENERATION_DURATION = Histogram("ml_generation_duration_seconds", "Frame generation duration", ["model", "status"])
GENERATION_TOTAL = Counter("ml_generation_total", "Total generations", ["model", "status"])
JOBS_IN_PROGRESS = Gauge("ml_jobs_in_progress", "ML jobs in progress")

MODELS = {
    "placeholder_v1": {"description": "Basic placeholder with text overlay", "color": (30, 30, 60)},
    "placeholder_v2": {"description": "Gradient placeholder with cinematic bars", "color": (20, 40, 80)},
    "placeholder_artistic": {"description": "Artistic style placeholder", "color": (60, 20, 40)},
}
DEFAULT_MODEL = "placeholder_v1"


class Settings(BaseSettings):
    gcs_endpoint: str = "http://gcs:4443"
    gcs_bucket: str = "dailycinema"
    redis_url: str = "redis://redis:6379/0"
    max_workers: int = 4
    batch_size: int = 8
    default_model: str = "placeholder_v1"

    class Config:
        env_file = ".env"


settings = Settings()

app = FastAPI(title="Daily Cinema ML Module", version="1.0.0")
Instrumentator(excluded_handlers=["/health/live", "/health/ready", "/metrics"]).instrument(app).expose(app)

jobs: dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=settings.max_workers)
model_cache: dict[str, bool] = {}


class GenerateRequest(BaseModel):
    job_id: str
    shot_id: str
    project_id: str
    prompt: str = ""
    model: str = "placeholder_v1"
    num_frames: int = 1


class JobStatus(BaseModel):
    job_id: str
    status: str
    frame_urls: list[str] = []
    model: str = ""
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


def warmup_model(model_name: str):
    if model_name in model_cache:
        return
    logger.info("Warming up model: %s", model_name)
    generate_placeholder_frame("warmup", "00000000", 0, model_name)
    model_cache[model_name] = True
    logger.info("Model %s warmed up", model_name)


def generate_placeholder_frame(prompt: str, shot_id: str, frame_num: int, model_name: str = DEFAULT_MODEL) -> bytes:
    model_config = MODELS.get(model_name, MODELS[DEFAULT_MODEL])
    base_color = model_config["color"]

    r_shift = (frame_num * 7) % 30
    g_shift = (frame_num * 11) % 30
    color = (base_color[0] + r_shift, base_color[1] + g_shift, base_color[2])

    img = Image.new("RGB", (1920, 1080), color=color)
    draw = ImageDraw.Draw(img)

    if model_name == "placeholder_v2":
        draw.rectangle([(0, 0), (1920, 120)], fill=(0, 0, 0))
        draw.rectangle([(0, 960), (1920, 1080)], fill=(0, 0, 0))

    draw.rectangle([(60, 60), (1860, 1020)], outline=(100, 200, 255), width=3)
    draw.text((150, 150), "DAILY CINEMA", fill=(255, 255, 255))
    draw.text((150, 250), f"Model: {model_name}", fill=(200, 200, 200))
    draw.text((150, 350), f"Shot: {shot_id[:8]}", fill=(200, 200, 200))
    draw.text((150, 450), f"Frame: {frame_num:03d}", fill=(200, 200, 200))
    draw.text((150, 550), f"Prompt: {prompt[:60]}", fill=(180, 180, 255))
    draw.text((150, 700), f"[ {model_config['description']} ]", fill=(255, 200, 100))

    if model_name == "placeholder_artistic":
        for i in range(20):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            r = random.randint(5, 30)
            c = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=c, outline=c)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_interpolated_frames(prompt: str, shot_id: str, num_frames: int, model_name: str) -> list[bytes]:
    frames = []
    for i in range(num_frames):
        frames.append(generate_placeholder_frame(prompt, shot_id, i + 1, model_name))
    return frames


def run_generation(job_id: str, shot_id: str, project_id: str, prompt: str, model: str, num_frames: int):
    start = time.monotonic()
    JOBS_IN_PROGRESS.inc()
    try:
        warmup_model(model)
        logger.info("Generating %d frame(s) for job %s with model %s", num_frames, job_id, model)

        frames = generate_interpolated_frames(prompt, shot_id, num_frames, model)

        client = get_gcs_client()
        bucket = ensure_bucket(client, settings.gcs_bucket)

        frame_urls = []
        for i, frame_data in enumerate(frames):
            blob_path = f"projects/{project_id}/ml/shot_{shot_id}/frame_{i + 1:03d}.png"
            blob = bucket.blob(blob_path)
            blob.upload_from_string(frame_data, content_type="image/png")
            frame_url = f"{settings.gcs_endpoint}/storage/v1/b/{settings.gcs_bucket}/o/{blob_path}?alt=media"
            frame_urls.append(frame_url)

        duration = (time.monotonic() - start) * 1000
        jobs[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "frame_urls": frame_urls,
            "model": model,
            "duration_ms": duration,
        }
        GENERATION_DURATION.labels(model=model, status="completed").observe(time.monotonic() - start)
        GENERATION_TOTAL.labels(model=model, status="completed").inc()
        logger.info("ML job %s completed in %.0fms", job_id, duration)
    except Exception as e:
        logger.exception("ML job %s failed: %s", job_id, e)
        GENERATION_DURATION.labels(model=model, status="failed").observe(time.monotonic() - start)
        GENERATION_TOTAL.labels(model=model, status="failed").inc()
        jobs[job_id] = {
            "job_id": job_id,
            "status": "failed",
            "frame_urls": [],
            "model": model,
            "duration_ms": 0,
        }
    finally:
        JOBS_IN_PROGRESS.dec()


@app.post("/generate", response_model=JobStatus)
async def generate(req: GenerateRequest):
    model = req.model if req.model in MODELS else DEFAULT_MODEL
    jobs[req.job_id] = {
        "job_id": req.job_id,
        "status": "processing",
        "frame_urls": [],
        "model": model,
        "duration_ms": 0,
    }
    executor.submit(run_generation, req.job_id, req.shot_id, req.project_id, req.prompt, model, req.num_frames)
    return JobStatus(**jobs[req.job_id])


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        return JobStatus(job_id=job_id, status="not_found")
    return JobStatus(**jobs[job_id])


@app.get("/models")
async def list_models():
    return {"models": {k: v["description"] for k, v in MODELS.items()}, "default": DEFAULT_MODEL}


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "models_cached": len(model_cache), "workers": settings.max_workers}


@app.get("/health")
async def health():
    return {"status": "ok"}
