from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.core.config import settings
from app.utils.crypto import hash_api_key
from tests.fixtures.clinical_data import (
    RECONCILE_REQUEST_CLEAR,
    RECONCILE_REQUEST_AGREEMENT,
    DATA_QUALITY_COMPLETE,
    DATA_QUALITY_MISSING_FIELDS,
    DATA_QUALITY_IMPLAUSIBLE_VITALS
)


client = TestClient(app)

# Generate the valid API key hash for use in tests
VALID_API_KEY_HASH = hash_api_key(settings.APP_API_KEY, settings.HASH_SALT)


class TestHealthEndpoint:
    def test_health_check_returns_200(self):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_has_status(self):
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_has_environment(self):
        response = client.get("/api/health")
        data = response.json()
        assert "environment" in data

    def test_health_check_has_cache_stats_when_enabled(self):
        response = client.get("/api/health")
        data = response.json()
        if settings.CACHE_ENABLED:
            assert "cache" in data


class TestReconcileEndpointAuth:
    def test_reconcile_requires_api_key(self):
        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_CLEAR.model_dump()
        )
        assert response.status_code == 401

    def test_reconcile_rejects_invalid_api_key(self):
        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_CLEAR.model_dump(),
            headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 401

    def test_reconcile_accepts_valid_api_key(self):
        with patch("app.api.routes.reconcile.reconcile_with_gemini") as mock_reconcile:
            mock_reconcile.return_value = MagicMock(
                reconciled_medication="Lisinopril 20mg once daily",
                confidence_score=0.95,
                reasoning="Most recent source from hospital EHR",
                recommended_actions=[],
                clinical_safety_check="PASSED"
            )

            response = client.post(
                "/api/reconcile/medication",
                json=RECONCILE_REQUEST_CLEAR.model_dump(),
                headers={"X-API-Key": VALID_API_KEY_HASH}
            )
            assert response.status_code == 200


class TestReconcileEndpointWithMock:
    @patch("app.api.routes.reconcile.reconcile_with_gemini")
    def test_reconcile_clear_winner(self, mock_reconcile):
        mock_reconcile.return_value = MagicMock(
            reconciled_medication="Lisinopril 20mg once daily",
            confidence_score=0.92,
            reasoning="Hospital EHR source is more recent (2024-03-15) and more reliable (high) than pharmacy record (2024-01-10, medium). Patient has hypertension and CKD, making dose escalation clinically plausible.",
            recommended_actions=["Confirm with patient at next visit"],
            clinical_safety_check="PASSED"
        )

        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_CLEAR.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reconciled_medication"] == "Lisinopril 20mg once daily"
        assert data["confidence_score"] >= 0.9
        assert data["clinical_safety_check"] == "PASSED"

    @patch("app.api.routes.reconcile.reconcile_with_gemini")
    def test_reconcile_all_sources_agree(self, mock_reconcile):
        mock_reconcile.return_value = MagicMock(
            reconciled_medication="Aspirin 81mg once daily",
            confidence_score=0.98,
            reasoning="All sources agree on the same medication and dosage. High confidence.",
            recommended_actions=[],
            clinical_safety_check="PASSED"
        )

        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_AGREEMENT.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reconciled_medication"] == "Aspirin 81mg once daily"
        assert data["confidence_score"] >= 0.95
        assert data["clinical_safety_check"] == "PASSED"

    @patch("app.api.routes.reconcile.reconcile_with_gemini")
    def test_reconcile_returns_required_fields(self, mock_reconcile):
        mock_reconcile.return_value = MagicMock(
            reconciled_medication="Test medication",
            confidence_score=0.85,
            reasoning="Test reasoning",
            recommended_actions=["Test action"],
            clinical_safety_check="FLAGGED"
        )

        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_CLEAR.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert "reconciled_medication" in data
        assert "confidence_score" in data
        assert "reasoning" in data
        assert "recommended_actions" in data
        assert "clinical_safety_check" in data


class TestDataQualityEndpointAuth:
    def test_data_quality_requires_api_key(self):
        response = client.post(
            "/api/validate/data-quality",
            json=DATA_QUALITY_COMPLETE.model_dump()
        )
        assert response.status_code == 401

    def test_data_quality_rejects_invalid_api_key(self):
        response = client.post(
            "/api/validate/data-quality",
            json=DATA_QUALITY_COMPLETE.model_dump(),
            headers={"X-API-Key": "wrong-key"}
        )
        assert response.status_code == 401


class TestDataQualityEndpointWithMock:
    @patch("app.api.routes.data_quality.evaluate_data_quality_with_gemini")
    def test_data_quality_complete_record(self, mock_evaluate):
        mock_evaluate.return_value = MagicMock(
            overall_score=92,
            breakdown=MagicMock(
                completeness=95,
                accuracy=95,
                timeliness=90,
                clinical_plausibility=88
            ),
            issues_detected=[]
        )

        response = client.post(
            "/api/validate/data-quality",
            json=DATA_QUALITY_COMPLETE.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] >= 85
        assert data["breakdown"]["completeness"] >= 90
        assert len(data["issues_detected"]) == 0

    @patch("app.api.routes.data_quality.evaluate_data_quality_with_gemini")
    def test_data_quality_missing_fields(self, mock_evaluate):
        mock_evaluate.return_value = MagicMock(
            overall_score=35,
            breakdown=MagicMock(
                completeness=25,
                accuracy=50,
                timeliness=0,
                clinical_plausibility=65
            ),
            issues_detected=[
                MagicMock(
                    field="demographics.dob",
                    issue="Missing date of birth",
                    severity="high"
                ),
                MagicMock(
                    field="last_updated",
                    issue="No timestamp available",
                    severity="medium"
                )
            ]
        )

        response = client.post(
            "/api/validate/data-quality",
            json=DATA_QUALITY_MISSING_FIELDS.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["overall_score"] < 50
        assert data["breakdown"]["completeness"] < 50
        assert len(data["issues_detected"]) > 0

    @patch("app.api.routes.data_quality.evaluate_data_quality_with_gemini")
    def test_data_quality_implausible_vitals(self, mock_evaluate):
        mock_evaluate.return_value = MagicMock(
            overall_score=58,
            breakdown=MagicMock(
                completeness=85,
                accuracy=75,
                timeliness=90,
                clinical_plausibility=35
            ),
            issues_detected=[
                MagicMock(
                    field="vital_signs.blood_pressure",
                    issue="Blood pressure 220/140 mmHg indicates hypertensive crisis",
                    severity="high"
                ),
                MagicMock(
                    field="vital_signs.heart_rate",
                    issue="Heart rate 145 bpm is abnormally high",
                    severity="medium"
                )
            ]
        )

        response = client.post(
            "/api/validate/data-quality",
            json=DATA_QUALITY_IMPLAUSIBLE_VITALS.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["breakdown"]["clinical_plausibility"] < 50
        assert any(issue["severity"] == "high" for issue in data["issues_detected"])

    @patch("app.api.routes.data_quality.evaluate_data_quality_with_gemini")
    def test_data_quality_returns_required_fields(self, mock_evaluate):
        mock_evaluate.return_value = MagicMock(
            overall_score=75,
            breakdown=MagicMock(
                completeness=80,
                accuracy=85,
                timeliness=70,
                clinical_plausibility=65
            ),
            issues_detected=[]
        )

        response = client.post(
            "/api/validate/data-quality",
            json=DATA_QUALITY_COMPLETE.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "breakdown" in data
        assert "completeness" in data["breakdown"]
        assert "accuracy" in data["breakdown"]
        assert "timeliness" in data["breakdown"]
        assert "clinical_plausibility" in data["breakdown"]
        assert "issues_detected" in data


class TestErrorHandling:
    @patch("app.api.routes.reconcile.reconcile_with_gemini")
    def test_reconcile_handles_rate_limit_error(self, mock_reconcile):
        from app.services.gemini_service import RateLimitError
        mock_reconcile.side_effect = RateLimitError("Rate limited")

        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_CLEAR.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 503
        assert "rate limit" in response.json()["detail"].lower()

    @patch("app.api.routes.reconcile.reconcile_with_gemini")
    def test_reconcile_handles_gemini_error(self, mock_reconcile):
        from app.services.gemini_service import GeminiError
        mock_reconcile.side_effect = GeminiError("API error")

        response = client.post(
            "/api/reconcile/medication",
            json=RECONCILE_REQUEST_CLEAR.model_dump(),
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 502
        assert "llm service error" in response.json()["detail"].lower()

    def test_reconcile_handles_invalid_request_data(self):
        invalid_request = {"invalid": "data"}

        response = client.post(
            "/api/reconcile/medication",
            json=invalid_request,
            headers={"X-API-Key": VALID_API_KEY_HASH}
        )

        assert response.status_code == 422
