from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

PUBLIC_PATHS = {"/health/live", "/health/ready", "/health", "/docs", "/openapi.json", "/metrics"}


async def verify_api_key(request: Request, api_key: str = Security(API_KEY_HEADER)):
    if request.url.path in PUBLIC_PATHS:
        return api_key
    if not api_key or api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key
