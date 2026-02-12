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

VISUAL_STYLES = {
    "ethereal_default": {
        "description": "Standard ethereal cosmic style - meditative calm",
        "base_color": (10, 10, 46),
        "gradient_start": (255, 105, 180),
        "gradient_end": (0, 206, 209),
        "accent": (138, 43, 226),
        "glow_color": (230, 230, 250),
        "fog_opacity": 60,
        "keywords": ["ethereal light", "spectral glow", "volumetric fog", "dreamlike atmosphere"],
    },
    "cosmic_cinematic": {
        "description": "High-contrast cinematic cosmic - epic transcendence",
        "base_color": (5, 5, 30),
        "gradient_start": (148, 0, 211),
        "gradient_end": (0, 191, 255),
        "accent": (255, 215, 0),
        "glow_color": (200, 200, 255),
        "fog_opacity": 80,
        "keywords": ["cosmic aura", "neon mist", "transcendent energy", "spectral glow"],
    },
    "luminous_dreamscape": {
        "description": "Soft dreamy pastels - dreamlike serenity",
        "base_color": (20, 15, 40),
        "gradient_start": (220, 208, 255),
        "gradient_end": (255, 179, 71),
        "accent": (255, 105, 180),
        "glow_color": (255, 240, 255),
        "fog_opacity": 100,
        "keywords": ["dreamlike atmosphere", "iridescent fabric", "ethereal light", "mythical harmony"],
    },
    "spectral_mythology": {
        "description": "Mythical creature-focused - ancient wisdom",
        "base_color": (8, 12, 35),
        "gradient_start": (64, 224, 208),
        "gradient_end": (255, 215, 0),
        "accent": (0, 206, 209),
        "glow_color": (180, 255, 230),
        "fog_opacity": 70,
        "keywords": ["mythical harmony", "spectral glow", "cosmic aura", "volumetric fog"],
    },
    "neon_ritual": {
        "description": "Ritualistic energy ceremony - spiritual ritual",
        "base_color": (15, 5, 30),
        "gradient_start": (138, 43, 226),
        "gradient_end": (255, 215, 0),
        "accent": (255, 20, 147),
        "glow_color": (200, 150, 255),
        "fog_opacity": 50,
        "keywords": ["transcendent energy", "neon mist", "cosmic aura", "spectral glow"],
    },
}

MODELS = {
    "placeholder_v1": {"description": "Basic placeholder with text overlay", "color": (30, 30, 60)},
    "placeholder_v2": {"description": "Gradient placeholder with cinematic bars", "color": (20, 40, 80)},
    "placeholder_artistic": {"description": "Artistic style placeholder", "color": (60, 20, 40)},
}
for style_name, style_cfg in VISUAL_STYLES.items():
    MODELS[style_name] = {"description": style_cfg["description"], "color": style_cfg["base_color"]}

DEFAULT_MODEL = "ethereal_default"
DEFAULT_VISUAL_STYLE = "ethereal_default"


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
    model: str = "ethereal_default"
    visual_style: str = "ethereal_default"
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


def _draw_spectral_gradient(img: Image.Image, style: dict, frame_num: int):
    width, height = img.size
    gs = style["gradient_start"]
    ge = style["gradient_end"]
    phase = (frame_num * 0.05) % 1.0
    pixels = img.load()
    for y in range(height):
        t = (y / height + phase) % 1.0
        r = int(gs[0] + (ge[0] - gs[0]) * t)
        g = int(gs[1] + (ge[1] - gs[1]) * t)
        b = int(gs[2] + (ge[2] - gs[2]) * t)
        for x in range(width):
            base = pixels[x, y]
            blend = 0.3
            nr = int(base[0] * (1 - blend) + r * blend)
            ng = int(base[1] * (1 - blend) + g * blend)
            nb = int(base[2] * (1 - blend) + b * blend)
            pixels[x, y] = (nr, ng, nb)


def _draw_fog_overlay(draw: ImageDraw.Draw, img: Image.Image, style: dict):
    fog_layer = Image.new("RGBA", img.size, (*style["glow_color"], style["fog_opacity"]))
    img.paste(Image.alpha_composite(img.convert("RGBA"), fog_layer).convert("RGB"))


def _draw_energy_particles(draw: ImageDraw.Draw, style: dict, frame_num: int):
    accent = style["accent"]
    glow = style["glow_color"]
    random.seed(frame_num * 42)
    for _ in range(40):
        x = random.randint(50, 1870)
        y = random.randint(50, 1030)
        r = random.randint(2, 12)
        c = accent if random.random() > 0.5 else glow
        alpha_c = (*c, random.randint(80, 200))
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=alpha_c[:3])
    for _ in range(8):
        x = random.randint(200, 1720)
        y = random.randint(200, 880)
        r = random.randint(30, 80)
        draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=(*glow, 20)[:3])


def _draw_vignette(draw: ImageDraw.Draw, img: Image.Image):
    w, h = img.size
    for i in range(80):
        alpha = int(2.5 * i)
        draw.rectangle([(i, i), (w - i, h - i)], outline=(0, 0, 0, alpha)[:3])


def _enrich_prompt(prompt: str, style: dict) -> str:
    keywords = style.get("keywords", [])
    enriched = prompt
    for kw in keywords:
        if kw.lower() not in prompt.lower():
            enriched = f"{enriched}, {kw}"
            break
    return enriched


def generate_placeholder_frame(prompt: str, shot_id: str, frame_num: int, model_name: str = DEFAULT_MODEL, visual_style: str = DEFAULT_VISUAL_STYLE) -> bytes:
    style = VISUAL_STYLES.get(visual_style)
    model_config = MODELS.get(model_name, MODELS[DEFAULT_MODEL])

    if style:
        base_color = style["base_color"]
        enriched_prompt = _enrich_prompt(prompt, style)
    else:
        base_color = model_config["color"]
        enriched_prompt = prompt

    r_shift = (frame_num * 7) % 30
    g_shift = (frame_num * 11) % 30
    color = (base_color[0] + r_shift, base_color[1] + g_shift, base_color[2])

    img = Image.new("RGB", (1920, 1080), color=color)
    draw = ImageDraw.Draw(img)

    if style:
        _draw_spectral_gradient(img, style, frame_num)
        draw = ImageDraw.Draw(img)
        _draw_energy_particles(draw, style, frame_num)
        _draw_vignette(draw, img)

    if model_name == "placeholder_v2":
        draw.rectangle([(0, 0), (1920, 120)], fill=(0, 0, 0))
        draw.rectangle([(0, 960), (1920, 1080)], fill=(0, 0, 0))

    border_color = style["accent"] if style else (100, 200, 255)
    draw.rectangle([(60, 60), (1860, 1020)], outline=border_color, width=2)

    text_color = style["glow_color"] if style else (255, 255, 255)
    draw.text((150, 150), "DAILY CINEMA", fill=text_color)
    draw.text((150, 250), f"Style: {visual_style}", fill=text_color)
    draw.text((150, 350), f"Shot: {shot_id[:8]}", fill=(200, 200, 200))
    draw.text((150, 450), f"Frame: {frame_num:03d}", fill=(200, 200, 200))
    draw.text((150, 550), f"Prompt: {enriched_prompt[:80]}", fill=border_color)

    desc = style["description"] if style else model_config["description"]
    draw.text((150, 700), f"[ {desc} ]", fill=(255, 200, 100))

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


def generate_interpolated_frames(prompt: str, shot_id: str, num_frames: int, model_name: str, visual_style: str = DEFAULT_VISUAL_STYLE) -> list[bytes]:
    frames = []
    for i in range(num_frames):
        frames.append(generate_placeholder_frame(prompt, shot_id, i + 1, model_name, visual_style))
    return frames


def run_generation(job_id: str, shot_id: str, project_id: str, prompt: str, model: str, num_frames: int, visual_style: str = DEFAULT_VISUAL_STYLE):
    start = time.monotonic()
    JOBS_IN_PROGRESS.inc()
    try:
        warmup_model(model)
        logger.info("Generating %d frame(s) for job %s with model %s style %s", num_frames, job_id, model, visual_style)

        frames = generate_interpolated_frames(prompt, shot_id, num_frames, model, visual_style)

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
    model = req.model
    if not model or model not in MODELS:
        logger.warning("Invalid model '%s' in generate request, falling back to '%s'", req.model, DEFAULT_MODEL)
        model = DEFAULT_MODEL
    jobs[req.job_id] = {
        "job_id": req.job_id,
        "status": "processing",
        "frame_urls": [],
        "model": model,
        "duration_ms": 0,
    }
    visual_style = req.visual_style
    if not visual_style or visual_style not in VISUAL_STYLES:
        logger.warning("Invalid visual_style '%s' in generate request, falling back to '%s'", req.visual_style, DEFAULT_VISUAL_STYLE)
        visual_style = DEFAULT_VISUAL_STYLE
    executor.submit(run_generation, req.job_id, req.shot_id, req.project_id, req.prompt, model, req.num_frames, visual_style)
    return JobStatus(**jobs[req.job_id])


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    if job_id not in jobs:
        return JobStatus(job_id=job_id, status="not_found")
    return JobStatus(**jobs[job_id])


@app.get("/models")
async def list_models():
    return {"models": {k: v["description"] for k, v in MODELS.items()}, "default": DEFAULT_MODEL}


@app.get("/styles")
async def list_styles():
    return {
        "styles": {k: {"description": v["description"], "keywords": v["keywords"]} for k, v in VISUAL_STYLES.items()},
        "default": DEFAULT_VISUAL_STYLE,
    }


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness():
    return {"status": "ready", "models_cached": len(model_cache), "workers": settings.max_workers}


@app.get("/health")
async def health():
    return {"status": "ok"}
