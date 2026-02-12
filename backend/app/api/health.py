import logging

from fastapi import APIRouter
from sqlalchemy import text

from app.models.database import engine
from app.services.redis_queue import redis_queue

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness():
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    checks = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        logger.error("Database readiness check failed: %s", e)
        checks["database"] = "error"

    try:
        if redis_queue._redis:
            await redis_queue.redis.ping()
            checks["redis"] = "ok"
        else:
            checks["redis"] = "not_connected"
    except Exception as e:
        logger.error("Redis readiness check failed: %s", e)
        checks["redis"] = "error"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}


@router.get("/health")
async def health():
    return {"status": "ok"}
