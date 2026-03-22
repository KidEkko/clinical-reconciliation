import pytest
from unittest.mock import patch, MagicMock
from app.services.gemini_service import (
    reconcile_with_gemini,
    evaluate_data_quality_with_gemini,
    RateLimitError,
    GeminiError,
    _generate_with_model,
    _generate_with_fallback_models
)
from app.models.reconcile import ReconcileMedicationResponse
from app.models.data_quality import DataQualityResponse
from tests.fixtures.clinical_data import (
    RECONCILE_REQUEST_CLEAR,
    DATA_QUALITY_COMPLETE
)
from google.genai.errors import ClientError, ServerError


class TestGenerateWithModel:
    @patch("app.services.gemini_service.g_client")
    def test_generate_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.text = '{"test": "data"}'
        mock_client.models.generate_content.return_value = mock_response

        result = _generate_with_model("test prompt", {}, "gemini-2.0-flash-exp")

        assert result == '{"test": "data"}'
        mock_client.models.generate_content.assert_called_once()

    @patch("app.services.gemini_service.g_client")
    def test_generate_rate_limit_error(self, mock_client):
        mock_error = ClientError("Rate limited", {})
        mock_error.status_code = 429
        mock_client.models.generate_content.side_effect = mock_error

        with pytest.raises(RateLimitError) as exc:
            _generate_with_model("test prompt", {}, "gemini-2.0-flash-exp")

        assert "Rate limit exceeded" in str(exc.value)

    @patch("app.services.gemini_service.g_client")
    def test_generate_server_error(self, mock_client):
        mock_error = ServerError("Server error", {})
        mock_client.models.generate_content.side_effect = mock_error

        with pytest.raises(GeminiError) as exc:
            _generate_with_model("test prompt", {}, "gemini-2.0-flash-exp")

        assert "service unavailable" in str(exc.value).lower()

    @patch("app.services.gemini_service.g_client")
    def test_generate_empty_response(self, mock_client):
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.models.generate_content.return_value = mock_response

        with pytest.raises(GeminiError) as exc:
            _generate_with_model("test prompt", {}, "gemini-2.0-flash-exp")

        assert "empty response" in str(exc.value).lower()


class TestGenerateWithFallback:
    @patch("app.services.gemini_service._generate_with_model")
    def test_fallback_first_model_succeeds(self, mock_generate):
        mock_generate.return_value = '{"test": "data"}'

        result = _generate_with_fallback_models("test prompt", {})

        assert result == '{"test": "data"}'
        assert mock_generate.call_count == 1

    @patch("app.services.gemini_service._generate_with_model")
    def test_fallback_tries_next_model_on_rate_limit(self, mock_generate):
        mock_generate.side_effect = [
            RateLimitError("Rate limited"),
            '{"test": "data"}'
        ]

        result = _generate_with_fallback_models("test prompt", {})

        assert result == '{"test": "data"}'
        assert mock_generate.call_count == 2

    @patch("app.services.gemini_service._generate_with_model")
    def test_fallback_raises_on_all_rate_limited(self, mock_generate):
        mock_generate.side_effect = RateLimitError("Rate limited")

        with pytest.raises(RateLimitError) as exc:
            _generate_with_fallback_models("test prompt", {})

        assert "All Gemini models rate limited" in str(exc.value)

    @patch("app.services.gemini_service._generate_with_model")
    def test_fallback_raises_immediately_on_gemini_error(self, mock_generate):
        mock_generate.side_effect = GeminiError("API error")

        with pytest.raises(GeminiError):
            _generate_with_fallback_models("test prompt", {})

        assert mock_generate.call_count == 1


class TestReconcileWithGemini:
    @patch("app.services.gemini_service._cache")
    @patch("app.services.gemini_service._generate_with_fallback_models")
    def test_reconcile_returns_valid_response(self, mock_generate, mock_cache):
        mock_cache.get.return_value = None
        mock_json = '''
        {
            "reconciled_medication": "Lisinopril 20mg once daily",
            "confidence_score": 0.92,
            "reasoning": "Hospital EHR is more recent and reliable",
            "recommended_actions": ["Confirm with patient"],
            "clinical_safety_check": "PASSED"
        }
        '''
        mock_generate.return_value = mock_json

        result = reconcile_with_gemini(RECONCILE_REQUEST_CLEAR)

        assert isinstance(result, ReconcileMedicationResponse)
        assert result.reconciled_medication == "Lisinopril 20mg once daily"
        assert result.confidence_score == 0.92
        assert result.clinical_safety_check == "PASSED"

    @patch("app.services.gemini_service._cache")
    @patch("app.services.gemini_service._generate_with_fallback_models")
    def test_reconcile_uses_cache(self, mock_generate, mock_cache):
        cached_json = '''
        {
            "reconciled_medication": "Cached medication",
            "confidence_score": 0.95,
            "reasoning": "From cache",
            "recommended_actions": [],
            "clinical_safety_check": "PASSED"
        }
        '''
        mock_cache.get.return_value = cached_json

        result = reconcile_with_gemini(RECONCILE_REQUEST_CLEAR)

        assert result.reconciled_medication == "Cached medication"
        mock_generate.assert_not_called()

    @patch("app.services.gemini_service._cache")
    @patch("app.services.gemini_service._generate_with_fallback_models")
    def test_reconcile_stores_in_cache(self, mock_generate, mock_cache):
        mock_cache.get.return_value = None
        mock_json = '''
        {
            "reconciled_medication": "New medication",
            "confidence_score": 0.88,
            "reasoning": "Generated",
            "recommended_actions": [],
            "clinical_safety_check": "PASSED"
        }
        '''
        mock_generate.return_value = mock_json

        result = reconcile_with_gemini(RECONCILE_REQUEST_CLEAR)

        assert result.reconciled_medication == "New medication"
        mock_cache.set.assert_called_once()


class TestEvaluateDataQualityWithGemini:
    @patch("app.services.gemini_service._cache")
    @patch("app.services.gemini_service._generate_with_fallback_models")
    def test_evaluate_returns_valid_response(self, mock_generate, mock_cache):
        mock_cache.get.return_value = None
        mock_json = '''
        {
            "overall_score": 92,
            "breakdown": {
                "completeness": 95,
                "accuracy": 95,
                "timeliness": 90,
                "clinical_plausibility": 88
            },
            "issues_detected": []
        }
        '''
        mock_generate.return_value = mock_json

        result = evaluate_data_quality_with_gemini(DATA_QUALITY_COMPLETE)

        assert isinstance(result, DataQualityResponse)
        assert result.overall_score == 92
        assert result.breakdown.completeness == 95
        assert len(result.issues_detected) == 0

    @patch("app.services.gemini_service._cache")
    @patch("app.services.gemini_service._generate_with_fallback_models")
    def test_evaluate_with_issues(self, mock_generate, mock_cache):
        mock_cache.get.return_value = None
        mock_json = '''
        {
            "overall_score": 65,
            "breakdown": {
                "completeness": 70,
                "accuracy": 75,
                "timeliness": 60,
                "clinical_plausibility": 55
            },
            "issues_detected": [
                {
                    "field": "demographics.dob",
                    "issue": "Missing date of birth",
                    "severity": "high"
                }
            ]
        }
        '''
        mock_generate.return_value = mock_json

        result = evaluate_data_quality_with_gemini(DATA_QUALITY_COMPLETE)

        assert result.overall_score == 65
        assert len(result.issues_detected) == 1
        assert result.issues_detected[0].severity == "high"

    @patch("app.services.gemini_service._cache")
    @patch("app.services.gemini_service._generate_with_fallback_models")
    def test_evaluate_uses_cache(self, mock_generate, mock_cache):
        cached_json = '''
        {
            "overall_score": 85,
            "breakdown": {
                "completeness": 85,
                "accuracy": 85,
                "timeliness": 85,
                "clinical_plausibility": 85
            },
            "issues_detected": []
        }
        '''
        mock_cache.get.return_value = cached_json

        result = evaluate_data_quality_with_gemini(DATA_QUALITY_COMPLETE)

        assert result.overall_score == 85
        mock_generate.assert_not_called()
