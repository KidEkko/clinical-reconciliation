"""
Example clinical test data for integration tests.
"""

from app.models.reconcile import ReconcileMedicationRequest, PatientContext, MedicationSource
from app.models.data_quality import DataQualityRequest, Demographics


# Patient contexts for reconciliation tests
PATIENT_CONTEXT_ELDERLY = PatientContext(
    age=72,
    conditions=["Hypertension", "Type 2 Diabetes", "Chronic Kidney Disease"],
    recent_labs={
        "creatinine": "1.8 mg/dL",
        "eGFR": "42 mL/min/1.73m²",
        "HbA1c": "7.2%"
    }
)

PATIENT_CONTEXT_YOUNG_HEALTHY = PatientContext(
    age=28,
    conditions=[],
    recent_labs={}
)

# Medication sources for reconciliation tests
MEDICATION_SOURCES_CLEAR_WINNER = [
    MedicationSource(
        system="Hospital EHR",
        medication="Lisinopril 20mg once daily",
        last_updated="2024-03-15",
        source_reliability="high"
    ),
    MedicationSource(
        system="Retail Pharmacy",
        medication="Lisinopril 10mg once daily",
        last_updated="2024-01-10",
        last_filled="2024-01-10",
        source_reliability="medium"
    )
]

MEDICATION_SOURCES_CONFLICT = [
    MedicationSource(
        system="Hospital EHR",
        medication="Metformin 1000mg twice daily",
        last_updated="2024-03-10",
        source_reliability="high"
    ),
    MedicationSource(
        system="Patient Portal",
        medication="Metformin 500mg twice daily",
        last_updated="2024-03-12",
        source_reliability="medium"
    ),
    MedicationSource(
        system="Primary Care Office",
        medication="Metformin 1000mg twice daily",
        last_updated="2024-03-10",
        source_reliability="high"
    )
]

MEDICATION_SOURCES_ALL_IDENTICAL = [
    MedicationSource(
        system="Hospital EHR",
        medication="Aspirin 81mg once daily",
        last_updated="2024-03-15",
        source_reliability="high"
    ),
    MedicationSource(
        system="Retail Pharmacy",
        medication="Aspirin 81mg once daily",
        last_updated="2024-03-14",
        last_filled="2024-03-14",
        source_reliability="high"
    )
]

# Complete reconciliation requests
RECONCILE_REQUEST_CLEAR = ReconcileMedicationRequest(
    patient_context=PATIENT_CONTEXT_ELDERLY,
    sources=MEDICATION_SOURCES_CLEAR_WINNER
)

RECONCILE_REQUEST_CONFLICT = ReconcileMedicationRequest(
    patient_context=PATIENT_CONTEXT_ELDERLY,
    sources=MEDICATION_SOURCES_CONFLICT
)

RECONCILE_REQUEST_AGREEMENT = ReconcileMedicationRequest(
    patient_context=PATIENT_CONTEXT_YOUNG_HEALTHY,
    sources=MEDICATION_SOURCES_ALL_IDENTICAL
)

# Demographics for data quality tests
DEMOGRAPHICS_COMPLETE = Demographics(
    name="John Doe",
    dob="1952-05-15",
    gender="male"
)

DEMOGRAPHICS_INCOMPLETE = Demographics(
    name="Jane Smith",
    dob=None,
    gender=None
)

# Data quality requests
DATA_QUALITY_COMPLETE = DataQualityRequest(
    demographics=DEMOGRAPHICS_COMPLETE,
    medications=["Lisinopril 20mg once daily", "Metformin 1000mg twice daily", "Aspirin 81mg once daily"],
    allergies=["Penicillin", "Sulfa drugs"],
    conditions=["Hypertension", "Type 2 Diabetes"],
    vital_signs={
        "blood_pressure": "138/82 mmHg",
        "heart_rate": "76 bpm",
        "temperature": "98.4 F",
        "respiratory_rate": "16 breaths/min"
    },
    last_updated="2024-03-15"
)

DATA_QUALITY_MISSING_FIELDS = DataQualityRequest(
    demographics=DEMOGRAPHICS_INCOMPLETE,
    medications=[],
    allergies=[],
    conditions=[],
    vital_signs={},
    last_updated=None
)

DATA_QUALITY_IMPLAUSIBLE_VITALS = DataQualityRequest(
    demographics=DEMOGRAPHICS_COMPLETE,
    medications=["Lisinopril 20mg once daily"],
    allergies=[],
    conditions=["Hypertension"],
    vital_signs={
        "blood_pressure": "220/140 mmHg",  # Crisis level
        "heart_rate": "145 bpm",  # Very high
        "temperature": "103.5 F",  # Fever
    },
    last_updated="2024-03-15"
)

DATA_QUALITY_STALE_DATA = DataQualityRequest(
    demographics=DEMOGRAPHICS_COMPLETE,
    medications=["Lisinopril 10mg once daily"],
    allergies=["Penicillin"],
    conditions=["Hypertension"],
    vital_signs={
        "blood_pressure": "128/78 mmHg",
        "heart_rate": "72 bpm"
    },
    last_updated="2021-06-10"  # Over 2 years old
)
