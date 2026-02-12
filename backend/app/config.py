from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://dailycinema:dailycinema@db:5432/dailycinema"
    database_url_sync: str = "postgresql+psycopg2://dailycinema:dailycinema@db:5432/dailycinema"
    gcs_endpoint: str = "http://gcs:4443"
    gcs_bucket: str = "dailycinema"
    ml_service_url: str = "http://ml:8001"
    unity_service_url: str = "http://unity:8002"

    class Config:
        env_file = ".env"


settings = Settings()
