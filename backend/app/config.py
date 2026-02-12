from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://dailycinema:dailycinema@db:5432/dailycinema"
    database_url_sync: str = "postgresql+psycopg2://dailycinema:dailycinema@db:5432/dailycinema"
    gcs_endpoint: str = "http://gcs:4443"
    gcs_bucket: str = "dailycinema"
    ml_service_url: str = "http://ml:8001"
    unity_service_url: str = "http://unity:8002"
    redis_url: str = "redis://redis:6379/0"

    api_key: str = "dc-prod-api-key-change-me"
    rate_limit: str = "60/minute"

    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    ml_job_max_retries: int = 3
    ml_job_retry_base_delay: float = 2.0
    render_job_max_retries: int = 3
    render_job_retry_base_delay: float = 3.0

    log_level: str = "INFO"
    environment: str = "production"
    acu_mode: str = "full"

    class Config:
        env_file = ".env"


settings = Settings()
