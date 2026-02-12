import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.config import settings
from app.logging_config import setup_logging
from app.models.database import engine, Base
from app.api.projects import router as projects_router
from app.api.health import router as health_router
from app.middleware.auth import verify_api_key
from app.services.redis_queue import redis_queue

setup_logging()
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created.")

    try:
        await redis_queue.connect()
        logger.info("Redis connected.")
    except Exception as e:
        logger.warning("Redis connection failed (non-fatal): %s", e)

    yield

    await redis_queue.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Daily Cinema API",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    excluded_handlers=["/health/live", "/health/ready", "/metrics"],
).instrument(app).expose(app, include_in_schema=True)

app.include_router(health_router)
app.include_router(projects_router)
