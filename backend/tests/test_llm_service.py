from app.models.reconcile import ReconcileMedicationRequest
from app.services import llm_service

from app.services.llm_service import build_reconcile_prompt

class MockResponse:
    def __init__(self, output_text: str):
        self.output_text = output_text


class MockResponsesClient:
    def create(self, **kwargs):
        return MockResponse(
            """
            {
              "reconciled_medication": "Metformin 500mg twice daily",
              "confidence_score": 0.87,
              "reasoning": "The primary care source is more recent than the hospital record, and the lower dose is plausible in the setting of reduced kidney function. The pharmacy record may reflect an older prescription.",
              "recommended_actions": [
                "Update the hospital medication list",
                "Confirm the active prescription with the pharmacy"
              ],
              "clinical_safety_check": "PASSED"
            }
            """
        )


class MockOpenAIClient:
    def __init__(self):
        self.responses = MockResponsesClient()


# TODO: Evaluate whether this test matters at all. Mocking responses like this always feels weird
def test_reconcile_with_llm_returns_valid_structured_response(monkeypatch):
    monkeypatch.setattr(llm_service, "client", MockOpenAIClient())

    payload = ReconcileMedicationRequest(
        patient_context={
            "age": 67,
            "conditions": ["Type 2 Diabetes", "Hypertension"],
            "recent_labs": {"eGFR": 45},
        },
        sources=[
            {
                "system": "Hospital EHR",
                "medication": "Metformin 1000mg twice daily",
                "last_updated": "2024-10-15",
                "source_reliability": "high",
            },
            {
                "system": "Primary Care",
                "medication": "Metformin 500mg twice daily",
                "last_updated": "2025-01-20",
                "source_reliability": "high",
            },
            {
                "system": "Pharmacy",
                "medication": "Metformin 1000mg daily",
                "last_filled": "2025-01-25",
                "source_reliability": "medium",
            },
        ],
    )

    result = llm_service.reconcile_with_llm(payload)

    assert result.reconciled_medication
    assert "Metformin" in result.reconciled_medication
    assert 0.0 <= result.confidence_score <= 1.0
    assert result.confidence_score >= 0.5

    assert result.reasoning
    assert isinstance(result.reasoning, str)
    assert len(result.reasoning) > 20

    assert isinstance(result.recommended_actions, list)
    assert len(result.recommended_actions) >= 1
    assert all(isinstance(action, str) and action.strip() for action in result.recommended_actions)

    assert result.clinical_safety_check in {"PASSED", "FLAGGED", "REQUIRES_REVIEW"}
