import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["styles"])

VALID_STYLES = [
    "ethereal_default",
    "cosmic_cinematic",
    "luminous_dreamscape",
    "spectral_mythology",
    "neon_ritual",
]

ML_KEYWORDS = {
    "ethereal_default": ["ethereal light", "spectral glow", "neon mist", "volumetric fog", "dreamlike atmosphere"],
    "cosmic_cinematic": ["cosmic aura", "transcendent energy", "neon mist", "spectral glow"],
    "luminous_dreamscape": ["dreamlike atmosphere", "iridescent fabric", "ethereal light", "mythical harmony"],
    "spectral_mythology": ["mythical harmony", "spectral glow", "cosmic aura", "volumetric fog"],
    "neon_ritual": ["transcendent energy", "neon mist", "cosmic aura", "spectral glow"],
}

HDRP_PRESETS = {
    "ethereal_default": {"bloom_intensity": 0.8, "fog_density": 0.15, "vignette_intensity": 0.25, "chromatic_aberration": 0.08},
    "cosmic_cinematic": {"bloom_intensity": 1.0, "fog_density": 0.25, "vignette_intensity": 0.35, "chromatic_aberration": 0.12},
    "luminous_dreamscape": {"bloom_intensity": 1.2, "fog_density": 0.30, "vignette_intensity": 0.20, "chromatic_aberration": 0.05},
    "spectral_mythology": {"bloom_intensity": 0.9, "fog_density": 0.20, "vignette_intensity": 0.30, "chromatic_aberration": 0.10},
    "neon_ritual": {"bloom_intensity": 1.1, "fog_density": 0.18, "vignette_intensity": 0.40, "chromatic_aberration": 0.15},
}

FFMPEG_PRESETS = {
    "ethereal_default": {"fps": 24, "preset": "medium", "crf": 20},
    "cosmic_cinematic": {"fps": 30, "preset": "slow", "crf": 18},
    "luminous_dreamscape": {"fps": 24, "preset": "medium", "crf": 19},
    "spectral_mythology": {"fps": 24, "preset": "medium", "crf": 20},
    "neon_ritual": {"fps": 30, "preset": "slow", "crf": 18},
}


class StyleValidateRequest(BaseModel):
    visual_style: str


class StyleValidateResponse(BaseModel):
    valid: bool
    visual_style: str
    resolved_style: str
    ml_keywords: list[str]
    hdrp_preset: dict
    ffmpeg_preset: dict
    acu_mode: str


@router.post("/styles/validate", response_model=StyleValidateResponse)
async def validate_style(payload: StyleValidateRequest):
    style = payload.visual_style
    is_valid = style in VALID_STYLES
    resolved = style if is_valid else "ethereal_default"

    return StyleValidateResponse(
        valid=is_valid,
        visual_style=style,
        resolved_style=resolved,
        ml_keywords=ML_KEYWORDS[resolved],
        hdrp_preset=HDRP_PRESETS[resolved],
        ffmpeg_preset=FFMPEG_PRESETS[resolved],
        acu_mode=settings.acu_mode,
    )


@router.get("/styles")
async def list_styles():
    return {
        "styles": VALID_STYLES,
        "default": "ethereal_default",
        "acu_mode": settings.acu_mode,
    }
