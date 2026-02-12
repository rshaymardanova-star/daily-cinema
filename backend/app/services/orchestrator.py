import asyncio
import json
import uuid
import logging

import httpx
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.database import async_session
from app.models.project import Project, Shot, MLJob, RenderJob

logger = logging.getLogger(__name__)


async def run_pipeline(project_id: uuid.UUID) -> None:
    logger.info("Starting pipeline for project %s", project_id)
    try:
        async with async_session() as db:
            result = await db.execute(
                select(Project)
                .options(selectinload(Project.shots))
                .where(Project.id == project_id)
            )
            project = result.scalar_one_or_none()
            if not project:
                logger.error("Project %s not found", project_id)
                return

            ml_tasks = []
            for shot in project.shots:
                ml_job = MLJob(shot_id=shot.id, status="pending")
                db.add(ml_job)
                await db.flush()
                ml_tasks.append((shot, ml_job))

            await db.commit()

            ml_results = await asyncio.gather(
                *[dispatch_ml_job(shot, ml_job) for shot, ml_job in ml_tasks],
                return_exceptions=True,
            )

            async with async_session() as db2:
                frame_map = {}
                all_success = True
                for (shot, ml_job), result in zip(ml_tasks, ml_results):
                    ml_job_db = await db2.get(MLJob, ml_job.id)
                    if isinstance(result, Exception):
                        logger.error("ML job %s failed: %s", ml_job.id, result)
                        ml_job_db.status = "failed"
                        ml_job_db.frame_urls = ""
                        all_success = False
                    else:
                        ml_job_db.status = "completed"
                        ml_job_db.frame_urls = json.dumps(result.get("frame_urls", []))
                        frame_map[str(shot.id)] = result.get("frame_urls", [])

                    shot_db = await db2.get(Shot, shot.id)
                    shot_db.status = ml_job_db.status
                await db2.commit()

                if not all_success:
                    proj = await db2.get(Project, project_id)
                    proj.status = "failed"
                    await db2.commit()
                    return

                scene_json = build_scene_json(project_id, project.shots, frame_map)

                render_job = RenderJob(
                    project_id=project_id,
                    status="pending",
                    scene_json=json.dumps(scene_json),
                )
                db2.add(render_job)
                await db2.commit()
                await db2.refresh(render_job)

                render_result = await dispatch_unity_render(render_job, scene_json)

                render_job_db = await db2.get(RenderJob, render_job.id)
                if isinstance(render_result, Exception) or not render_result:
                    render_job_db.status = "failed"
                    proj = await db2.get(Project, project_id)
                    proj.status = "failed"
                else:
                    render_job_db.status = "completed"
                    render_job_db.video_url = render_result.get("video_url", "")
                    proj = await db2.get(Project, project_id)
                    proj.status = "completed"

                await db2.commit()
                logger.info("Pipeline completed for project %s", project_id)

    except Exception as e:
        logger.exception("Pipeline failed for project %s: %s", project_id, e)
        try:
            async with async_session() as db:
                proj = await db.get(Project, project_id)
                if proj:
                    proj.status = "failed"
                    await db.commit()
        except Exception:
            logger.exception("Failed to update project status")


async def dispatch_ml_job(shot: Shot, ml_job: MLJob) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ml_service_url}/generate",
            json={
                "job_id": str(ml_job.id),
                "shot_id": str(shot.id),
                "project_id": str(shot.project_id),
                "prompt": shot.prompt,
            },
        )
        response.raise_for_status()
        result = response.json()

        job_id = result.get("job_id", str(ml_job.id))
        for _ in range(60):
            status_resp = await client.get(f"{settings.ml_service_url}/status/{job_id}")
            status_resp.raise_for_status()
            status_data = status_resp.json()
            if status_data["status"] == "completed":
                return status_data
            if status_data["status"] == "failed":
                raise RuntimeError(f"ML job {job_id} failed")
            await asyncio.sleep(1)

        raise TimeoutError(f"ML job {job_id} timed out")


def build_scene_json(
    project_id: uuid.UUID, shots: list[Shot], frame_map: dict
) -> dict:
    scene_shots = []
    for shot in sorted(shots, key=lambda s: s.order):
        scene_shots.append(
            {
                "shot_id": str(shot.id),
                "order": shot.order,
                "prompt": shot.prompt,
                "frame_urls": frame_map.get(str(shot.id), []),
            }
        )
    return {
        "project_id": str(project_id),
        "shots": scene_shots,
    }


async def dispatch_unity_render(render_job: RenderJob, scene_json: dict) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.unity_service_url}/render",
            json={
                "job_id": str(render_job.id),
                "project_id": str(render_job.project_id),
                "scene": scene_json,
            },
        )
        response.raise_for_status()
        result = response.json()

        job_id = result.get("job_id", str(render_job.id))
        for _ in range(120):
            status_resp = await client.get(
                f"{settings.unity_service_url}/status/{job_id}"
            )
            status_resp.raise_for_status()
            status_data = status_resp.json()
            if status_data["status"] == "completed":
                return status_data
            if status_data["status"] == "failed":
                raise RuntimeError(f"Render job {job_id} failed")
            await asyncio.sleep(1)

        raise TimeoutError(f"Render job {job_id} timed out")
