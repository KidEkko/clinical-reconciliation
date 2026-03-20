import json
import os

from openai import OpenAI
from google import genai
from google.genai import types

from app.models.reconcile import (
    ReconcileMedicationRequest,
    ReconcileMedicationResponse,
)
from app.models.data_quality import (
    DataQualityRequest,
    DataQualityResponse,
)
from app.utils.response_schema import (
    RECONCILE_RESPONSE_SCHEMA,
    DATA_QUALITY_RESPONSE_SCHEMA
)

g_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GPT_MODEL = "gpt-5.4"

def build_reconcile_prompt(payload: ReconcileMedicationRequest) -> str:
    payload_json = json.dumps(payload.model_dump(mode="json"), indent=2)

    return f"""
You are assisting with a clinical data reconciliation application.

Your task is to determine the most likely current medication record from conflicting sources.

Instructions:
- Use only the information provided in the input.
- Do not invent facts, diagnoses, lab values, medications, or patient history.
- Prefer more recent and more reliable sources when conflicts exist.
- Consider whether the patient context makes a dose change or source discrepancy plausible.
- If the evidence is mixed or uncertain, lower the confidence score and recommend human follow-up.
- Keep the reasoning concise, specific, and clinician-friendly.
- Return only JSON matching the required schema.

Input:
{payload_json}
""".strip()


def reconcile_with_llm(
    payload: ReconcileMedicationRequest,
    model: str = GPT_MODEL,
) -> ReconcileMedicationResponse:
    prompt = build_reconcile_prompt(payload)

    response = client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "reconcile_medication_response",
                "schema": RECONCILE_RESPONSE_SCHEMA,
                "strict": True,
            }
        },
    )

    raw_json = response.output_text
    return ReconcileMedicationResponse.model_validate_json(raw_json)


def reconcile_with_gemini_llm(
    payload: ReconcileMedicationRequest,
    model: str = "gemini-3-flash-preview",
) -> ReconcileMedicationResponse:
    prompt = build_reconcile_prompt(payload)

    response = g_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ReconcileMedicationResponse.model_json_schema(),
            temperature=0.2,
        ),
    )

    raw_json = response.text
    return ReconcileMedicationResponse.model_validate_json(raw_json)

def build_data_quality_prompt(payload: DataQualityRequest) -> str:
    payload_json = payload.model_dump_json(indent=2)

    return f"""
You are assisting with a clinical data quality review application.

Your task is to evaluate the quality of a patient record and return a structured assessment.

Instructions:
- Use only the information provided in the input.
- Do not invent facts, diagnoses, medications, allergies, or timestamps.
- Score the record across these dimensions:
  - completeness
  - accuracy
  - timeliness
  - clinical_plausibility
- Each dimension score must be an integer from 0 to 100.
- overall_score must also be an integer from 0 to 100.
- Flag concrete problems in issues_detected.
- Prefer specific field paths in the "field" value, like:
  - demographics.dob
  - vital_signs.blood_pressure
  - last_updated
- Keep issue descriptions concise and human-readable.
- If a value is clearly implausible, reflect that strongly in the scores.
- Return only valid JSON matching the required schema.

Evaluation guidance:
- completeness: are important fields present and meaningfully populated?
- accuracy: do values appear internally valid and well-formed?
- timeliness: does the record appear stale based on last_updated?
- clinical_plausibility: are values medically plausible and non-contradictory?

Input:
{payload_json}
""".strip()

def evaluate_data_quality_with_llm(
    payload: DataQualityRequest,
    model: str = GPT_MODEL,
) -> DataQualityResponse:
    prompt = build_data_quality_prompt(payload)

    response = client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "data_quality_response",
                "schema": DATA_QUALITY_RESPONSE_SCHEMA,
                "strict": True,
            }
        },
    )

    raw_json = response.output_text
    return DataQualityResponse.model_validate_json(raw_json)


def evaluate_data_quality_with_gemini_llm(
    payload: DataQualityRequest,
    model: str = "gemini-3-flash-preview",
) -> DataQualityResponse:
    prompt = build_data_quality_prompt(payload)

    response = g_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DataQualityResponse.model_json_schema(),
            temperature=0.2,
        ),
    )

    raw_json = response.text
    return DataQualityResponse.model_validate_json(raw_json)