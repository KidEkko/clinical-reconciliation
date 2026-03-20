from fastapi import APIRouter, HTTPException
from app.models.reconcile import (
    ReconcileMedicationRequest,
    ReconcileMedicationResponse,
)
from app.services.llm_service import reconcile_with_gemini_llm

router = APIRouter(prefix="/api/reconcile", tags=["reconcile"])


@router.post("/medication", response_model=ReconcileMedicationResponse)
def reconcile_medication(payload: ReconcileMedicationRequest) -> ReconcileMedicationResponse:
    try:
        return reconcile_with_gemini_llm(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM reconciliation failed: {str(exc)}")