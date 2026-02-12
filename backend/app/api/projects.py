import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.database import get_db
from app.models.project import Project, Shot, MLJob, RenderJob
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectDetailResponse,
    TimelineResponse,
    ProjectStatusResponse,
    ShotResponse,
    MLJobResponse,
    RenderJobResponse,
)
from app.services.orchestrator import run_pipeline

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(name=payload.name, description=payload.description, visual_style=payload.visual_style)
    db.add(project)
    await db.flush()

    for i, shot_data in enumerate(payload.shots):
        shot = Shot(
            project_id=project.id,
            prompt=shot_data.prompt,
            order=shot_data.order if shot_data.order else i,
        )
        db.add(shot)

    if not payload.shots:
        shot = Shot(project_id=project.id, prompt="default shot", order=0)
        db.add(shot)

    await db.commit()
    await db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.shots), selectinload(Project.render_jobs))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/timeline", response_model=TimelineResponse)
async def get_timeline(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.shots), selectinload(Project.render_jobs))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return TimelineResponse(
        project_id=project.id,
        shots=project.shots,
        render_jobs=project.render_jobs,
    )


@router.post("/{project_id}/render", response_model=ProjectResponse)
async def start_render(
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.status == "rendering":
        raise HTTPException(status_code=409, detail="Project is already rendering")

    project.status = "rendering"
    await db.commit()
    await db.refresh(project)

    background_tasks.add_task(run_pipeline, project_id)
    return project


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_status(project_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.shots).selectinload(Shot.ml_jobs),
            selectinload(Project.render_jobs),
        )
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    all_ml_jobs = []
    shot_responses = []
    for shot in project.shots:
        shot_responses.append(ShotResponse.model_validate(shot))
        for ml_job in shot.ml_jobs:
            all_ml_jobs.append(MLJobResponse.model_validate(ml_job))

    render_responses = [RenderJobResponse.model_validate(rj) for rj in project.render_jobs]

    return ProjectStatusResponse(
        project_id=project.id,
        project_status=project.status,
        visual_style=project.visual_style,
        resolved_style=project.visual_style,
        shots=shot_responses,
        ml_jobs=all_ml_jobs,
        render_jobs=render_responses,
    )
