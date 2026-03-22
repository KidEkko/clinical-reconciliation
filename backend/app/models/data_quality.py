from typing import Literal, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.utils.validators import validate_iso_date

SeverityScale = Literal["high", "medium", "low"]

class Demographics(BaseModel):
    name: str | None = Field(
        None,
        min_length=1,
        description="Patient Name",
    )
    dob: str | None = Field(
        None,
        min_length=1,
        description="Patient Date Of Birth",
    )
    gender: str | None = Field(
        None,
        min_length=1,
        description="Patient Gender",
    )

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v: str | None) -> str | None:
        try:
            return validate_iso_date(v)
        except ValueError:
            raise ValueError("Date of birth must be in ISO 8601 format")

class DataQualityRequest(BaseModel):
    demographics: Demographics
    medications: list[str] = Field(
        default_factory=list,
        description="List of known patient medications",
    )
    allergies: list[str] = Field(
        default_factory=list,
        description="List of known patient allergies",
    )
    conditions: list[str] = Field(
        default_factory=list,
        description="List of known patient conditions",
    )
    vital_signs: dict[str, Any] = Field(
        default_factory=dict,
        description="Patient vital signs as key/value pairs",
    )
    last_updated: str | None = Field(
        None,
        min_length=1,
        description="Date of most recent update to patient records",
    )

    @field_validator("last_updated")
    @classmethod
    def validate_last_updated(cls, v: str | None) -> str | None:
        try:
            return validate_iso_date(v)
        except ValueError:
            raise ValueError("Last updated must be in ISO 8601 format")

class DataQualityBreakdown(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    completeness: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall completeness of data",
    )
    accuracy: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall accuracy of data",
    )
    timeliness: int = Field(
        ...,
        ge=0,
        le=100,
        # TODO: update this
        description="Recency of data",
    )
    clinical_plausibility: int = Field(
        ...,
        ge=0,
        le=100,
        description="Clinical plausibility and coherence of the data",
    )

class DataQualityIssue(BaseModel):
    field: str = Field(
      ...,
      min_length=1,
      description="Field from data quality request that contains an issue"
    )
    issue: str = Field(
        ...,
        min_length=1,
        description="Concise human-readable reason for the issue"
    )
    severity: SeverityScale = Field(
        ..., 
        # TODO: update this
        description="Impact of the issue on data quality",
    )

class DataQualityResponse(BaseModel):
    overall_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall confidence score for data quality",
    )
    breakdown: DataQualityBreakdown
    issues_detected: list[DataQualityIssue] = Field(
        default_factory=list,
        description="List of known patient conditions",
    )
