import uuid
from datetime import datetime

from pydantic import BaseModel


class ShotCreate(BaseModel):
    prompt: str = ""
    order: int = 0


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    shots: list[ShotCreate] = []


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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RenderJobResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    video_url: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    status: str
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
