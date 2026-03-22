from fastapi import APIRouter, HTTPException, Depends
from pydantic import ValidationError

from app.core.auth import require_api_key
from app.core.logging import get_logger
from app.models.data_quality import (
    DataQualityRequest,
    DataQualityResponse,
)
from app.services.gemini_service import evaluate_data_quality_with_gemini, RateLimitError, GeminiError

router = APIRouter(prefix="/api/validate", tags=["data-quality"])
logger = get_logger(__name__)


@router.post("/data-quality", response_model=DataQualityResponse)
def validate_data_quality(
    payload: DataQualityRequest,
    _: str = Depends(require_api_key)
) -> DataQualityResponse:
    try:
        return evaluate_data_quality_with_gemini(payload)
    except RateLimitError as exc:
        logger.warning("Rate limit error in data quality endpoint")
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to rate limiting. Please try again later."
        ) from exc
    except GeminiError as exc:
        logger.error(f"Gemini error in data quality endpoint: {str(exc)}")
        raise HTTPException(
            status_code=502,
            detail="External LLM service error. Please try again."
        ) from exc
    except ValidationError as exc:
        logger.error(f"Validation error in data quality endpoint: {str(exc)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid response from LLM: {str(exc)}"
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error in data quality endpoint")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during data quality validation."
        ) from exc
