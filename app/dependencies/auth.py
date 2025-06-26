from fastapi import Header, HTTPException, Security
from fastapi.security import APIKeyHeader
from app.config import settings



async def verify_api_key(x_api_key: str = Security(APIKeyHeader(name="X-API-Key"))):
    if x_api_key != settings.secret.key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
