import io
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from PIL import Image, ImageDraw, ImageFont
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

app = FastAPI(title="Daily Cinema ML Module", version="0.1.0")

jobs: dict[str, dict] = {}
executor = ThreadPoolExecutor(max_workers=4)


class GenerateRequest(BaseModel):
    job_id: str
    shot_id: str
    project_id: str
    prompt: str = ""


class JobStatus(BaseModel):
    job_id: str
    status: str
    frame_urls: list[str] = []


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


def generate_placeholder_frame(prompt: str, shot_id: str, frame_num: int) -> bytes:
    img = Image.new("RGB", (1280, 720), color=(30, 30, 60))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(40, 40), (1240, 680)], outline=(100, 200, 255), width=3)
    draw.text((100, 100), "DAILY CINEMA", fill=(255, 255, 255))
    draw.text((100, 200), f"Shot: {shot_id[:8]}", fill=(200, 200, 200))
    draw.text((100, 300), f"Frame: {frame_num:03d}", fill=(200, 200, 200))
    draw.text((100, 400), f"Prompt: {prompt[:50]}", fill=(180, 180, 255))
    draw.text((100, 550), "[ ML Placeholder Frame ]", fill=(255, 200, 100))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def run_generation(job_id: str, shot_id: str, project_id: str, prompt: str):
    try:
        logger.info("Generating frame for job %s", job_id)
        frame_data = generate_placeholder_frame(prompt, shot_id, 1)

        client = get_gcs_client()
        bucket = ensure_bucket(client, settings.gcs_bucket)

        blob_path = f"projects/{project_id}/ml/shot_{shot_id}/frame_001.png"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(frame_data, content_type="image/png")

        frame_url = f"{settings.gcs_endpoint}/storage/v1/b/{settings.gcs_bucket}/o/{blob_path}?alt=media"

        jobs[job_id] = {
            "job_id": job_id,
            "status": "completed",
            "frame_urls": [frame_url],
        }
        logger.info("ML job %s completed", job_id)
    except Exception as e:
        logger.exception("ML job %s failed: %s", job_id, e)
        jobs[job_id] = {
            "job_id": job_id,
            "status": "failed",
            "frame_urls": [],
        }


@app.post("/generate", response_model=JobStatus)
async def generate(req: GenerateRequest):
    jobs[req.job_id] = {
        "job_id": req.job_id,
        "status": "processing",
        "frame_urls": [],
    }
    executor.submit(run_generation, req.job_id, req.shot_id, req.project_id, req.prompt)
    return JobStatus(**jobs[req.job_id])


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        return JobStatus(job_id=job_id, status="not_found")
    return JobStatus(**jobs[job_id])


@app.get("/health")
async def health():
    return {"status": "ok"}
