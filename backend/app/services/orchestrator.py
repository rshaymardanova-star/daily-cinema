import asyncio
import json
import time
import uuid
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.database import async_session
from app.models.project import Project, Shot, MLJob, RenderJob
from app.schemas.project import VALID_VISUAL_STYLES, DEFAULT_VISUAL_STYLE
from app.metrics import (
    ML_JOB_DURATION,
    RENDER_DURATION,
    ORCHESTRATOR_LATENCY,
    ERROR_COUNTER,
    JOBS_IN_PROGRESS,
    JOBS_TOTAL,
    RETRY_COUNTER,
    ACU_BUDGET_USED,
    ACU_BUDGET_WARNINGS,
    ACU_FALLBACK_EVENTS,
)

logger = logging.getLogger(__name__)

ACU_COSTS = {
    "ml_job": 10.0,
    "render_job": 25.0,
    "render_preview": 5.0,
    "mock_job": 0.1,
}


class ACUBudgetTracker:
    def __init__(self, project_id: str, budget: float, warning_threshold: float):
        self.project_id = project_id
        self.budget = budget
        self.warning_threshold = warning_threshold
        self.used = 0.0
        self.fallback_triggered = False

    def consume(self, cost_type: str) -> bool:
        cost = ACU_COSTS.get(cost_type, 1.0)
        self.used += cost
        ACU_BUDGET_USED.labels(project_id=self.project_id).set(self.used)

        ratio = self.used / self.budget if self.budget > 0 else 1.0
        if ratio >= 1.0 and not self.fallback_triggered:
            self.fallback_triggered = True
            ACU_FALLBACK_EVENTS.inc()
            logger.warning(
                "[ACU Budget] Project %s exceeded budget (%.1f/%.1f). Falling back to light mode.",
                self.project_id, self.used, self.budget,
            )
            return True
        if ratio >= self.warning_threshold:
            ACU_BUDGET_WARNINGS.inc()
            logger.warning(
                "[ACU Budget] Project %s approaching limit (%.1f/%.1f = %.0f%%)",
                self.project_id, self.used, self.budget, ratio * 100,
            )
        return False

    @property
    def remaining(self) -> float:
        return max(0.0, self.budget - self.used)


async def run_pipeline(project_id: uuid.UUID) -> None:
    pipeline_start = time.monotonic()
    logger.info("Starting pipeline for project %s", project_id)
    JOBS_IN_PROGRESS.labels(job_type="pipeline").inc()
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

            raw_style = project.visual_style or ""
            if raw_style not in VALID_VISUAL_STYLES:
                logger.warning(
                    "Project %s has invalid visual_style '%s', falling back to '%s'",
                    project_id, raw_style, DEFAULT_VISUAL_STYLE,
                )
                visual_style = DEFAULT_VISUAL_STYLE
            else:
                visual_style = raw_style

            budget = ACUBudgetTracker(
                str(project_id), settings.acu_budget_per_task, settings.acu_warning_threshold
            )
            use_light = settings.acu_mode == "light"
            if use_light:
                logger.info("[ACU_MODE=light] Pipeline for project %s — ML and Unity will use mock mode", project_id)

            ml_tasks = []
            for shot in project.shots:
                ml_job = MLJob(shot_id=shot.id, status="pending")
                db.add(ml_job)
                await db.flush()
                ml_tasks.append((shot, ml_job))

            await db.commit()

        ml_results = await asyncio.gather(
            *[dispatch_ml_job_with_retry(shot, ml_job, visual_style) for shot, ml_job in ml_tasks],
            return_exceptions=True,
        )

        async with async_session() as db2:
            frame_map = {}
            all_success = True
            for (shot, ml_job), ml_result in zip(ml_tasks, ml_results):
                cost_type = "mock_job" if use_light else "ml_job"
                exceeded = budget.consume(cost_type)
                if exceeded and not use_light:
                    use_light = True
                    logger.warning("[ACU Budget] Switching remaining jobs to light mode for project %s", project_id)

                ml_job_db = await db2.get(MLJob, ml_job.id)
                if isinstance(ml_result, Exception):
                    logger.error("ML job %s failed: %s", ml_job.id, ml_result)
                    ml_job_db.status = "failed"
                    ml_job_db.error_message = str(ml_result)
                    ml_job_db.frame_urls = ""
                    ml_job_db.completed_at = datetime.now(timezone.utc)
                    all_success = False
                    JOBS_TOTAL.labels(job_type="ml", status="failed").inc()
                    ERROR_COUNTER.labels(component="ml", error_type=type(ml_result).__name__).inc()
                else:
                    ml_job_db.status = "completed"
                    ml_job_db.frame_urls = json.dumps(ml_result.get("frame_urls", []))
                    ml_job_db.completed_at = datetime.now(timezone.utc)
                    frame_map[str(shot.id)] = ml_result.get("frame_urls", [])
                    JOBS_TOTAL.labels(job_type="ml", status="completed").inc()

                shot_db = await db2.get(Shot, shot.id)
                shot_db.status = ml_job_db.status
            await db2.commit()

            if not all_success:
                proj = await db2.get(Project, project_id)
                proj.status = "failed"
                proj.error_message = "One or more ML jobs failed"
                await db2.commit()
                return

            scene_json = build_scene_json(project_id, project.shots, frame_map, visual_style)

            render_job = RenderJob(
                project_id=project_id,
                status="pending",
                scene_json=json.dumps(scene_json),
            )
            db2.add(render_job)
            await db2.commit()
            await db2.refresh(render_job)

            render_cost = "mock_job" if use_light else "render_job"
            budget.consume(render_cost)

            render_result = await dispatch_unity_render_with_retry(render_job, scene_json, visual_style)

            render_job_db = await db2.get(RenderJob, render_job.id)
            if isinstance(render_result, Exception) or not render_result:
                render_job_db.status = "failed"
                render_job_db.error_message = str(render_result) if isinstance(render_result, Exception) else "Empty result"
                render_job_db.completed_at = datetime.now(timezone.utc)
                proj = await db2.get(Project, project_id)
                proj.status = "failed"
                proj.error_message = "Render job failed"
                JOBS_TOTAL.labels(job_type="render", status="failed").inc()
                ERROR_COUNTER.labels(component="render", error_type="render_failure").inc()
            else:
                render_job_db.status = "completed"
                render_job_db.video_url = render_result.get("video_url", "")
                render_job_db.completed_at = datetime.now(timezone.utc)
                proj = await db2.get(Project, project_id)
                proj.status = "completed"
                JOBS_TOTAL.labels(job_type="render", status="completed").inc()

            await db2.commit()
            logger.info(
                "Pipeline completed for project %s (ACU budget: %.1f/%.1f used)",
                project_id, budget.used, budget.budget,
            )

    except Exception as e:
        logger.exception("Pipeline failed for project %s: %s", project_id, e)
        ERROR_COUNTER.labels(component="orchestrator", error_type=type(e).__name__).inc()
        try:
            async with async_session() as db:
                proj = await db.get(Project, project_id)
                if proj:
                    proj.status = "failed"
                    proj.error_message = str(e)
                    await db.commit()
        except Exception:
            logger.exception("Failed to update project status")
    finally:
        JOBS_IN_PROGRESS.labels(job_type="pipeline").dec()
        elapsed = time.monotonic() - pipeline_start
        ORCHESTRATOR_LATENCY.observe(elapsed)


async def dispatch_ml_job_with_retry(shot: Shot, ml_job: MLJob, visual_style: str = "ethereal_default") -> dict:
    max_retries = settings.ml_job_max_retries
    base_delay = settings.ml_job_retry_base_delay

    for attempt in range(max_retries + 1):
        try:
            start = time.monotonic()
            JOBS_IN_PROGRESS.labels(job_type="ml").inc()
            try:
                result = await dispatch_ml_job(shot, ml_job, visual_style)
                ML_JOB_DURATION.labels(status="completed").observe(time.monotonic() - start)
                return result
            finally:
                JOBS_IN_PROGRESS.labels(job_type="ml").dec()
        except Exception as e:
            ML_JOB_DURATION.labels(status="failed").observe(time.monotonic() - start)
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "ML job %s attempt %d/%d failed: %s. Retrying in %.1fs",
                    ml_job.id, attempt + 1, max_retries + 1, e, delay,
                )
                RETRY_COUNTER.labels(job_type="ml").inc()
                async with async_session() as db:
                    ml_job_db = await db.get(MLJob, ml_job.id)
                    if ml_job_db:
                        ml_job_db.retry_count = attempt + 1
                        await db.commit()
                await asyncio.sleep(delay)
            else:
                logger.error("ML job %s exhausted all retries", ml_job.id)
                raise


async def dispatch_ml_job(shot: Shot, ml_job: MLJob, visual_style: str = "ethereal_default") -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.ml_service_url}/generate",
            json={
                "job_id": str(ml_job.id),
                "shot_id": str(shot.id),
                "project_id": str(shot.project_id),
                "prompt": shot.prompt,
                "visual_style": visual_style,
                "model": visual_style,
            },
        )
        response.raise_for_status()
        resp_data = response.json()

        job_id = resp_data.get("job_id", str(ml_job.id))
        for _ in range(120):
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
    project_id: uuid.UUID, shots: list[Shot], frame_map: dict, visual_style: str = "ethereal_default"
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
        "visual_style": visual_style,
        "shots": scene_shots,
    }


async def dispatch_unity_render_with_retry(render_job: RenderJob, scene_json: dict, visual_style: str = "ethereal_default") -> dict:
    max_retries = settings.render_job_max_retries
    base_delay = settings.render_job_retry_base_delay

    for attempt in range(max_retries + 1):
        try:
            start = time.monotonic()
            JOBS_IN_PROGRESS.labels(job_type="render").inc()
            try:
                result = await dispatch_unity_render(render_job, scene_json, visual_style)
                RENDER_DURATION.labels(status="completed").observe(time.monotonic() - start)
                return result
            finally:
                JOBS_IN_PROGRESS.labels(job_type="render").dec()
        except Exception as e:
            RENDER_DURATION.labels(status="failed").observe(time.monotonic() - start)
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    "Render job %s attempt %d/%d failed: %s. Retrying in %.1fs",
                    render_job.id, attempt + 1, max_retries + 1, e, delay,
                )
                RETRY_COUNTER.labels(job_type="render").inc()
                async with async_session() as db:
                    rj = await db.get(RenderJob, render_job.id)
                    if rj:
                        rj.retry_count = attempt + 1
                        await db.commit()
                await asyncio.sleep(delay)
            else:
                logger.error("Render job %s exhausted all retries", render_job.id)
                raise


async def dispatch_unity_render(render_job: RenderJob, scene_json: dict, visual_style: str = "ethereal_default") -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.unity_service_url}/render",
            json={
                "job_id": str(render_job.id),
                "project_id": str(render_job.project_id),
                "scene": scene_json,
                "visual_style": visual_style,
                "template": visual_style,
            },
        )
        response.raise_for_status()
        resp_data = response.json()

        job_id = resp_data.get("job_id", str(render_job.id))
        for _ in range(180):
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
