import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ShotCreate(BaseModel):
    prompt: str = ""
    order: int = 0


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=5000)
    shots: list[ShotCreate] = Field(default_factory=list, max_length=100)


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
    status: str
    error_message: str = ""
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


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
    shots: list[ShotResponse]
    ml_jobs: list[MLJobResponse]
    render_jobs: list[RenderJobResponse]
