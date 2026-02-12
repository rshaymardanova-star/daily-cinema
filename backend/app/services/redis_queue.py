import json
import logging
import uuid

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

PIPELINE_QUEUE = "dailycinema:pipeline:queue"
DLQ_QUEUE = "dailycinema:pipeline:dlq"
JOB_PREFIX = "dailycinema:job:"


class RedisQueue:
    def __init__(self):
        self._redis: aioredis.Redis | None = None

    async def connect(self):
        self._redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
        await self._redis.ping()
        logger.info("Connected to Redis")

    async def disconnect(self):
        if self._redis:
            await self._redis.aclose()
            logger.info("Disconnected from Redis")

    @property
    def redis(self) -> aioredis.Redis:
        if not self._redis:
            raise RuntimeError("Redis not connected")
        return self._redis

    async def enqueue_pipeline(self, project_id: str, idempotency_key: str | None = None) -> str:
        job_id = idempotency_key or str(uuid.uuid4())
        existing = await self.redis.get(f"{JOB_PREFIX}{job_id}")
        if existing:
            logger.info("Duplicate pipeline job %s, skipping", job_id)
            return job_id

        job_data = {
            "job_id": job_id,
            "project_id": project_id,
            "retry_count": 0,
            "status": "queued",
        }
        await self.redis.set(f"{JOB_PREFIX}{job_id}", json.dumps(job_data), ex=86400)
        await self.redis.lpush(PIPELINE_QUEUE, json.dumps(job_data))
        logger.info("Enqueued pipeline job %s for project %s", job_id, project_id)
        return job_id

    async def dequeue_pipeline(self, timeout: int = 5) -> dict | None:
        result = await self.redis.brpop(PIPELINE_QUEUE, timeout=timeout)
        if result:
            _, data = result
            return json.loads(data)
        return None

    async def send_to_dlq(self, job_data: dict, error: str):
        job_data["status"] = "dead"
        job_data["error"] = error
        await self.redis.lpush(DLQ_QUEUE, json.dumps(job_data))
        await self.redis.set(
            f"{JOB_PREFIX}{job_data['job_id']}", json.dumps(job_data), ex=604800
        )
        logger.warning("Sent job %s to DLQ: %s", job_data["job_id"], error)

    async def update_job_status(self, job_id: str, status: str):
        raw = await self.redis.get(f"{JOB_PREFIX}{job_id}")
        if raw:
            job_data = json.loads(raw)
            job_data["status"] = status
            await self.redis.set(f"{JOB_PREFIX}{job_id}", json.dumps(job_data), ex=86400)

    async def get_job(self, job_id: str) -> dict | None:
        raw = await self.redis.get(f"{JOB_PREFIX}{job_id}")
        if raw:
            return json.loads(raw)
        return None

    async def get_queue_size(self) -> int:
        return await self.redis.llen(PIPELINE_QUEUE)

    async def get_dlq_size(self) -> int:
        return await self.redis.llen(DLQ_QUEUE)


redis_queue = RedisQueue()
