from fastapi import APIRouter, HTTPException

from app.models.data_quality import (
    DataQualityRequest,
    DataQualityResponse,
)
from app.services.llm_service import evaluate_data_quality_with_llm

router = APIRouter(prefix="/api/validate", tags=["data-quality"])

@router.post("/data-quality", response_model=DataQualityResponse)
def validate_data_quality(payload: DataQualityRequest) -> DataQualityResponse:
    try:
        return evaluate_data_quality_with_llm(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM evaluation failed: {str(exc)}")