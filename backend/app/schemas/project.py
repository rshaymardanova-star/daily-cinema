import logging
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger(__name__)

VALID_VISUAL_STYLES = {
    "ethereal_default",
    "cosmic_cinematic",
    "luminous_dreamscape",
    "spectral_mythology",
    "neon_ritual",
}
DEFAULT_VISUAL_STYLE = "ethereal_default"


class ShotCreate(BaseModel):
    prompt: str = ""
    order: int = 0


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=5000)
    visual_style: str = Field("ethereal_default", max_length=100)
    shots: list[ShotCreate] = Field(default_factory=list, max_length=100)

    @field_validator("visual_style")
    @classmethod
    def validate_visual_style(cls, v: str) -> str:
        if not v or v not in VALID_VISUAL_STYLES:
            logger.warning("Invalid visual_style '%s', falling back to '%s'", v, DEFAULT_VISUAL_STYLE)
            return DEFAULT_VISUAL_STYLE
        return v


class ShotResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    order: int
    prompt: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MLJobResponse(BaseModel):
    id: uuid.UUID
    shot_id: uuid.UUID
    status: str
    frame_urls: str
    retry_count: int = 0
    error_message: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RenderJobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    video_url: str
    retry_count: int = 0
    error_message: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    visual_style: str = "ethereal_default"
    resolved_style: str = ""
    status: str
    error_message: str = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def set_resolved_style(self):
        if not self.resolved_style:
            self.resolved_style = self.visual_style
        return self


class ProjectDetailResponse(ProjectResponse):
    shots: list[ShotResponse] = []
    render_jobs: list[RenderJobResponse] = []


class TimelineResponse(BaseModel):
    project_id: uuid.UUID
    shots: list[ShotResponse]
    render_jobs: list[RenderJobResponse]


class ProjectStatusResponse(BaseModel):
    project_id: uuid.UUID
    project_status: str
    visual_style: str = "ethereal_default"
    resolved_style: str = ""
    shots: list[ShotResponse]
    ml_jobs: list[MLJobResponse]
    render_jobs: list[RenderJobResponse]

    @model_validator(mode="after")
    def set_resolved_style(self):
        if not self.resolved_style:
            self.resolved_style = self.visual_style
        return self
