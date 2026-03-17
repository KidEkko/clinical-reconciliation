from fastapi import Header, HTTPException
from app.core.config import APP_API_KEY

def require_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")