from typing import Literal, Any
from pydantic import BaseModel, Field


Rating = Literal["PASSED", "FLAGGED", "REQUIRES_REVIEW"]
SourceReliability = Literal["high", "medium", "low"]


class PatientContext(BaseModel):
    age: int = Field(
        ..., 
        ge=0, 
        description="Patient age in years"
    )
    conditions: list[str] = Field(
        default_factory=list,
        description="Known patient conditions relevant to reconciliation",
    )

    # TODO: Confirm Any doesn't cause issues
    recent_labs: dict[str, Any] = Field(
        default_factory=dict,
        description="Recent lab results as key/value pairs",
    )


class MedicationSource(BaseModel):
    system: str = Field(
        ..., 
        min_length=1, 
        description="Name of the source system"
    )
    medication: str = Field(
        ...,
        min_length=1,
        description="Medication text exactly as provided by the source",
    )
    last_updated: str | None = Field(
        default=None,
        description="Last clinical update date in ISO format when available",
    )
    last_filled: str | None = Field(
        default=None,
        description="Last pharmacy fill date in ISO format when available",
    )
    source_reliability: SourceReliability = Field(
        ...,
        description="Relative trust level assigned to the source",
    )


class ReconcileMedicationRequest(BaseModel):
    patient_context: PatientContext
    sources: list[MedicationSource] = Field(
        ...,
        min_length=1,
        description="Conflicting medication records from different sources",
    )


class ReconcileMedicationResponse(BaseModel):
    reconciled_medication: str = Field(
        ...,
        min_length=1,
        description="Most likely current medication record",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score from 0.0 to 1.0",
    )
    reasoning: str = Field(
        ...,
        min_length=1,
        description="Concise human-readable clinical reasoning",
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Recommended follow-up actions",
    )
    clinical_safety_check: Rating = Field(
        ...,
        description="High-level safety assessment for the reconciliation result",
    )