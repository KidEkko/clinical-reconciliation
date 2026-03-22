import pytest
from pydantic import ValidationError
from app.models.reconcile import (
    PatientContext,
    MedicationSource,
    ReconcileMedicationRequest,
    ReconcileMedicationResponse,
)


class TestPatientContextValidation:
    def test_valid_age(self):
        context = PatientContext(age=45)
        assert context.age == 45

    def test_age_at_min_boundary(self):
        context = PatientContext(age=0)
        assert context.age == 0

    def test_age_at_max_boundary(self):
        context = PatientContext(age=150)
        assert context.age == 150

    def test_age_below_min(self):
        with pytest.raises(ValidationError) as exc:
            PatientContext(age=-1)
        assert "greater than or equal to 0" in str(exc.value)

    def test_age_above_max(self):
        with pytest.raises(ValidationError) as exc:
            PatientContext(age=151)
        assert "less than or equal to 150" in str(exc.value)

    def test_empty_lists_default(self):
        context = PatientContext(age=45)
        assert context.conditions == []
        assert context.recent_labs == {}


class TestMedicationSourceValidation:
    def test_valid_last_updated_iso_format(self):
        source = MedicationSource(
            system="EHR",
            medication="Lisinopril 10mg",
            last_updated="2024-03-15",
            source_reliability="high"
        )
        assert source.last_updated == "2024-03-15"

    def test_valid_last_updated_with_time(self):
        source = MedicationSource(
            system="EHR",
            medication="Lisinopril 10mg",
            last_updated="2024-03-15T14:30:00",
            source_reliability="high"
        )
        assert source.last_updated == "2024-03-15T14:30:00"

    def test_valid_last_updated_with_timezone(self):
        source = MedicationSource(
            system="EHR",
            medication="Lisinopril 10mg",
            last_updated="2024-03-15T14:30:00Z",
            source_reliability="high"
        )
        assert source.last_updated == "2024-03-15T14:30:00Z"

    def test_invalid_last_updated_format(self):
        with pytest.raises(ValidationError) as exc:
            MedicationSource(
                system="EHR",
                medication="Lisinopril 10mg",
                last_updated="03/15/2024",
                source_reliability="high"
            )
        assert "Date must be in ISO 8601 format" in str(exc.value)

    def test_valid_last_filled_iso_format(self):
        source = MedicationSource(
            system="Pharmacy",
            medication="Lisinopril 10mg",
            last_filled="2024-03-10",
            source_reliability="high"
        )
        assert source.last_filled == "2024-03-10"

    def test_invalid_last_filled_format(self):
        with pytest.raises(ValidationError) as exc:
            MedicationSource(
                system="Pharmacy",
                medication="Lisinopril 10mg",
                last_filled="03/10/2024",
                source_reliability="high"
            )
        assert "Date must be in ISO 8601 format" in str(exc.value)

    def test_none_dates_allowed(self):
        source = MedicationSource(
            system="EHR",
            medication="Lisinopril 10mg",
            last_updated=None,
            last_filled=None,
            source_reliability="high"
        )
        assert source.last_updated is None
        assert source.last_filled is None

    def test_valid_source_reliability_values(self):
        for reliability in ["high", "medium", "low"]:
            source = MedicationSource(
                system="EHR",
                medication="Lisinopril 10mg",
                source_reliability=reliability
            )
            assert source.source_reliability == reliability

    def test_invalid_source_reliability(self):
        with pytest.raises(ValidationError) as exc:
            MedicationSource(
                system="EHR",
                medication="Lisinopril 10mg",
                source_reliability="critical"
            )
        assert "Input should be 'high', 'medium' or 'low'" in str(exc.value)

    def test_empty_system_rejected(self):
        with pytest.raises(ValidationError) as exc:
            MedicationSource(
                system="",
                medication="Lisinopril 10mg",
                source_reliability="high"
            )
        assert "at least 1 character" in str(exc.value)

    def test_empty_medication_rejected(self):
        with pytest.raises(ValidationError) as exc:
            MedicationSource(
                system="EHR",
                medication="",
                source_reliability="high"
            )
        assert "at least 1 character" in str(exc.value)


class TestReconcileMedicationRequestValidation:
    def test_valid_request(self):
        req = ReconcileMedicationRequest(
            patient_context=PatientContext(age=65),
            sources=[
                MedicationSource(
                    system="EHR",
                    medication="Lisinopril 10mg",
                    source_reliability="high"
                ),
                MedicationSource(
                    system="Pharmacy",
                    medication="Lisinopril 20mg",
                    source_reliability="medium"
                )
            ]
        )
        assert len(req.sources) == 2

    def test_empty_sources_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ReconcileMedicationRequest(
                patient_context=PatientContext(age=65),
                sources=[]
            )
        assert "at least 1 item" in str(exc.value)

    def test_single_source_allowed(self):
        req = ReconcileMedicationRequest(
            patient_context=PatientContext(age=65),
            sources=[
                MedicationSource(
                    system="EHR",
                    medication="Lisinopril 10mg",
                    source_reliability="high"
                )
            ]
        )
        assert len(req.sources) == 1


class TestReconcileMedicationResponseValidation:
    def test_valid_response(self):
        response = ReconcileMedicationResponse(
            reconciled_medication="Lisinopril 10mg daily",
            confidence_score=0.85,
            reasoning="Most recent prescription from reliable source",
            recommended_actions=["Verify with patient"],
            clinical_safety_check="PASSED"
        )
        assert response.confidence_score == 0.85

    def test_confidence_score_at_min_boundary(self):
        response = ReconcileMedicationResponse(
            reconciled_medication="Lisinopril 10mg daily",
            confidence_score=0.0,
            reasoning="Low confidence",
            clinical_safety_check="REQUIRES_REVIEW"
        )
        assert response.confidence_score == 0.0

    def test_confidence_score_at_max_boundary(self):
        response = ReconcileMedicationResponse(
            reconciled_medication="Lisinopril 10mg daily",
            confidence_score=1.0,
            reasoning="High confidence",
            clinical_safety_check="PASSED"
        )
        assert response.confidence_score == 1.0

    def test_confidence_score_below_min(self):
        with pytest.raises(ValidationError) as exc:
            ReconcileMedicationResponse(
                reconciled_medication="Lisinopril 10mg daily",
                confidence_score=-0.1,
                reasoning="Invalid",
                clinical_safety_check="PASSED"
            )
        assert "greater than or equal to 0" in str(exc.value)

    def test_confidence_score_above_max(self):
        with pytest.raises(ValidationError) as exc:
            ReconcileMedicationResponse(
                reconciled_medication="Lisinopril 10mg daily",
                confidence_score=1.1,
                reasoning="Invalid",
                clinical_safety_check="PASSED"
            )
        assert "less than or equal to 1" in str(exc.value)

    def test_valid_clinical_safety_check_values(self):
        for rating in ["PASSED", "FLAGGED", "REQUIRES_REVIEW"]:
            response = ReconcileMedicationResponse(
                reconciled_medication="Lisinopril 10mg daily",
                confidence_score=0.85,
                reasoning="Test",
                clinical_safety_check=rating
            )
            assert response.clinical_safety_check == rating

    def test_invalid_clinical_safety_check(self):
        with pytest.raises(ValidationError) as exc:
            ReconcileMedicationResponse(
                reconciled_medication="Lisinopril 10mg daily",
                confidence_score=0.85,
                reasoning="Test",
                clinical_safety_check="APPROVED"
            )
        assert "Input should be 'PASSED', 'FLAGGED' or 'REQUIRES_REVIEW'" in str(exc.value)

    def test_empty_reconciled_medication_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ReconcileMedicationResponse(
                reconciled_medication="",
                confidence_score=0.85,
                reasoning="Test",
                clinical_safety_check="PASSED"
            )
        assert "at least 1 character" in str(exc.value)

    def test_empty_reasoning_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ReconcileMedicationResponse(
                reconciled_medication="Lisinopril 10mg daily",
                confidence_score=0.85,
                reasoning="",
                clinical_safety_check="PASSED"
            )
        assert "at least 1 character" in str(exc.value)

    def test_empty_recommended_actions_default(self):
        response = ReconcileMedicationResponse(
            reconciled_medication="Lisinopril 10mg daily",
            confidence_score=0.85,
            reasoning="Test",
            clinical_safety_check="PASSED"
        )
        assert response.recommended_actions == []
