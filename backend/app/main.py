from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.routes.reconcile import router as reconcile_router
from app.api.routes.data_quality import router as data_quality_router

setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION
)

logger.info(f"Starting {settings.API_TITLE} in {settings.ENVIRONMENT} mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    from app.services.gemini_service import _cache

    health_data = {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }

    if _cache:
        health_data["cache"] = _cache.stats()

    return health_data


app.include_router(reconcile_router)
app.include_router(data_quality_router)
