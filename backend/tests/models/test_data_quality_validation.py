import pytest
from pydantic import ValidationError
from app.models.data_quality import (
    Demographics,
    DataQualityRequest,
    DataQualityBreakdown,
    DataQualityIssue,
    DataQualityResponse,
)


class TestDemographicsValidation:
    def test_valid_dob_iso_format(self):
        demo = Demographics(
            name="John Doe",
            dob="2000-01-15",
            gender="male"
        )
        assert demo.dob == "2000-01-15"

    def test_valid_dob_with_time(self):
        demo = Demographics(
            name="Jane Doe",
            dob="2000-01-15T10:30:00",
            gender="female"
        )
        assert demo.dob == "2000-01-15T10:30:00"

    def test_valid_dob_with_timezone(self):
        demo = Demographics(
            name="Jane Doe",
            dob="2000-01-15T10:30:00Z",
            gender="female"
        )
        assert demo.dob == "2000-01-15T10:30:00Z"

    def test_invalid_dob_format(self):
        with pytest.raises(ValidationError) as exc:
            Demographics(
                name="John Doe",
                dob="01/15/2000",
                gender="male"
            )
        assert "Date of birth must be in ISO 8601 format" in str(exc.value)

    def test_invalid_dob_random_string(self):
        with pytest.raises(ValidationError) as exc:
            Demographics(
                name="John Doe",
                dob="not-a-date",
                gender="male"
            )
        assert "Date of birth must be in ISO 8601 format" in str(exc.value)

    def test_none_dob_allowed(self):
        demo = Demographics(name="John Doe", dob=None, gender="male")
        assert demo.dob is None


class TestDataQualityRequestValidation:
    def test_valid_last_updated_iso_format(self):
        req = DataQualityRequest(
            demographics=Demographics(name="John Doe"),
            last_updated="2024-03-15"
        )
        assert req.last_updated == "2024-03-15"

    def test_valid_last_updated_with_time(self):
        req = DataQualityRequest(
            demographics=Demographics(name="John Doe"),
            last_updated="2024-03-15T14:30:00"
        )
        assert req.last_updated == "2024-03-15T14:30:00"

    def test_valid_last_updated_with_timezone(self):
        req = DataQualityRequest(
            demographics=Demographics(name="John Doe"),
            last_updated="2024-03-15T14:30:00Z"
        )
        assert req.last_updated == "2024-03-15T14:30:00Z"

    def test_invalid_last_updated_format(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityRequest(
                demographics=Demographics(name="John Doe"),
                last_updated="03/15/2024"
            )
        assert "Last updated must be in ISO 8601 format" in str(exc.value)

    def test_none_last_updated_allowed(self):
        req = DataQualityRequest(
            demographics=Demographics(name="John Doe"),
            last_updated=None
        )
        assert req.last_updated is None

    def test_empty_lists_default(self):
        req = DataQualityRequest(
            demographics=Demographics(name="John Doe")
        )
        assert req.medications == []
        assert req.allergies == []
        assert req.conditions == []
        assert req.vital_signs == {}


class TestDataQualityBreakdownValidation:
    def test_valid_scores(self):
        breakdown = DataQualityBreakdown(
            completeness=85,
            accuracy=90,
            timeliness=75,
            clinical_plausibility=80
        )
        assert breakdown.completeness == 85

    def test_score_at_min_boundary(self):
        breakdown = DataQualityBreakdown(
            completeness=0,
            accuracy=0,
            timeliness=0,
            clinical_plausibility=0
        )
        assert breakdown.completeness == 0

    def test_score_at_max_boundary(self):
        breakdown = DataQualityBreakdown(
            completeness=100,
            accuracy=100,
            timeliness=100,
            clinical_plausibility=100
        )
        assert breakdown.completeness == 100

    def test_score_below_min(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityBreakdown(
                completeness=-1,
                accuracy=90,
                timeliness=75,
                clinical_plausibility=80
            )
        assert "greater than or equal to 0" in str(exc.value)

    def test_score_above_max(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityBreakdown(
                completeness=101,
                accuracy=90,
                timeliness=75,
                clinical_plausibility=80
            )
        assert "less than or equal to 100" in str(exc.value)


class TestDataQualityIssueValidation:
    def test_valid_severity_values(self):
        for severity in ["high", "medium", "low"]:
            issue = DataQualityIssue(
                field="medications",
                issue="Missing dosage",
                severity=severity
            )
            assert issue.severity == severity

    def test_invalid_severity_value(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityIssue(
                field="medications",
                issue="Missing dosage",
                severity="critical"
            )
        assert "Input should be 'high', 'medium' or 'low'" in str(exc.value)

    def test_empty_field_rejected(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityIssue(
                field="",
                issue="Missing dosage",
                severity="high"
            )
        assert "at least 1 character" in str(exc.value)

    def test_empty_issue_rejected(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityIssue(
                field="medications",
                issue="",
                severity="high"
            )
        assert "at least 1 character" in str(exc.value)


class TestDataQualityResponseValidation:
    def test_valid_response(self):
        response = DataQualityResponse(
            overall_score=85,
            breakdown=DataQualityBreakdown(
                completeness=80,
                accuracy=90,
                timeliness=85,
                clinical_plausibility=85
            ),
            issues_detected=[
                DataQualityIssue(
                    field="medications",
                    issue="Missing dosage",
                    severity="medium"
                )
            ]
        )
        assert response.overall_score == 85
        assert len(response.issues_detected) == 1

    def test_overall_score_boundaries(self):
        response = DataQualityResponse(
            overall_score=0,
            breakdown=DataQualityBreakdown(
                completeness=0,
                accuracy=0,
                timeliness=0,
                clinical_plausibility=0
            )
        )
        assert response.overall_score == 0

        response = DataQualityResponse(
            overall_score=100,
            breakdown=DataQualityBreakdown(
                completeness=100,
                accuracy=100,
                timeliness=100,
                clinical_plausibility=100
            )
        )
        assert response.overall_score == 100

    def test_overall_score_out_of_range(self):
        with pytest.raises(ValidationError) as exc:
            DataQualityResponse(
                overall_score=101,
                breakdown=DataQualityBreakdown(
                    completeness=100,
                    accuracy=100,
                    timeliness=100,
                    clinical_plausibility=100
                )
            )
        assert "less than or equal to 100" in str(exc.value)

    def test_empty_issues_list_default(self):
        response = DataQualityResponse(
            overall_score=95,
            breakdown=DataQualityBreakdown(
                completeness=95,
                accuracy=95,
                timeliness=95,
                clinical_plausibility=95
            )
        )
        assert response.issues_detected == []
