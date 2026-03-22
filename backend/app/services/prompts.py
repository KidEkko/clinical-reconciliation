from app.models.reconcile import ReconcileMedicationRequest
from app.models.data_quality import DataQualityRequest


def build_reconcile_prompt(payload: ReconcileMedicationRequest) -> str:
    """
    Build the structured prompt for medication reconciliation.
    Uses explicit criteria to prevent model confusion about conflict resolution.
    """
    payload_json = payload.model_dump_json(indent=2)

    return f"""
You are assisting with a clinical data reconciliation application.

Your task is to determine the most likely current medication record from conflicting sources.

Core Instructions:
- Use only the information provided in the input.
- Do not invent facts, diagnoses, lab values, medications, or patient history.
- Keep the reasoning concise, specific, and clinician-friendly.
- Return only JSON matching the required schema.

Conflict Resolution Priority:
1. Most recent timestamp (last_updated > last_filled)
2. Source reliability (high > medium > low)
3. Clinical context compatibility (patient age, conditions, recent labs)
4. Consistency with patient history

Confidence Score Guidance:
- 0.9-1.0: All sources agree, or one clearly authoritative recent source
- 0.7-0.8: Recent reliable source contradicts older/less reliable sources
- 0.5-0.6: Sources equally recent/reliable but conflicting
- 0.3-0.4: Contradictory information, unclear which is correct
- 0.0-0.2: Insufficient or highly contradictory information

Clinical Safety Check:
- "PASSED": Reconciliation is clear and clinically reasonable
- "FLAGGED": Minor concern (e.g., dosage change without clear reason)
- "REQUIRES_REVIEW": Significant conflict, contradictory medications, or safety concern

Edge Cases:
- All sources identical → confidence 0.95+, safety "PASSED"
- Sources differ only in dosage → prefer most recent, flag for verification
- Contradictory medications → confidence < 0.6, safety "REQUIRES_REVIEW"
- All sources >1 year old → reduce confidence by 0.1-0.2, flag timeliness

Input:
{payload_json}
""".strip()


def build_data_quality_prompt(payload: DataQualityRequest) -> str:
    """
    Build the structured prompt for data quality evaluation.
    Uses explicit scoring rubrics to prevent confusion about what each dimension measures.
    """
    payload_json = payload.model_dump_json(indent=2)

    return f"""
You are assisting with a clinical data quality review application.

Your task is to evaluate the quality of a patient record and return a structured assessment.

Core Instructions:
- Use only the information provided in the input.
- Do not invent facts, diagnoses, medications, allergies, or timestamps.
- Each dimension score must be an integer from 0 to 100.
- overall_score must also be an integer from 0 to 100.
- Flag concrete problems in issues_detected with specific field paths.
- Keep issue descriptions concise and human-readable.
- Return only valid JSON matching the required schema.

Completeness (0-100): Measures presence and meaningfulness of data
- 90-100: All critical fields present with meaningful values (name, DOB, medications if relevant, key vitals)
- 70-89: Critical fields present, some important fields missing (allergies, conditions)
- 50-69: Core demographics present, but significant clinical data missing
- 30-49: Only basic demographics present, most clinical data absent
- 0-29: Critical fields missing or empty (missing name or DOB)

Critical fields: demographics.name, demographics.dob, demographics.gender
Important fields: medications (if applicable), allergies, conditions, vital_signs

Accuracy (0-100): Assesses validity and consistency of values
- 90-100: All values well-formed and consistent (valid date formats, reasonable numeric ranges)
- 70-89: Minor formatting issues or edge-case values (age 0, borderline vitals)
- 50-69: Some values poorly formatted or inconsistent (invalid dates, contradictory data)
- 30-49: Multiple invalid values or clear data entry errors
- 0-29: Majority of values malformed or nonsensical

Timeliness (0-100): Evaluates data recency
- 90-100: Updated within last 30 days
- 70-89: Updated 1-3 months ago
- 50-69: Updated 3-12 months ago
- 30-49: Updated 1-3 years ago
- 0-29: Updated >3 years ago or no timestamp available

Clinical Plausibility (0-100): Measures medical coherence
- 90-100: All values medically plausible and internally consistent
- 70-89: Values plausible but edge cases (very high/low vitals for specific conditions)
- 50-69: Some questionable values (BP 180/100 without hypertension diagnosis)
- 30-49: Multiple implausible values or contradictions
- 0-29: Life-incompatible values (BP 300/200, age 200, etc.)

Vital Sign Reference Ranges:
- Blood Pressure: 90-140/60-90 mmHg (normal), >180/120 (crisis), <90/60 (hypotension)
- Heart Rate: 60-100 bpm (normal adult at rest)
- Temperature: 36.1-37.2°C or 97-99°F (normal)
- Respiratory Rate: 12-20 breaths/min (normal adult)

Issue Severity Guidelines:
- "high": Missing critical fields or life-threatening values
- "medium": Missing important fields or concerning values (BP 160/100)
- "low": Missing optional fields or edge-case values

Field Path Format:
- Use dot notation: demographics.dob, vital_signs.blood_pressure, last_updated

Input:
{payload_json}
""".strip()
