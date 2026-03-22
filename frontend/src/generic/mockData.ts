import type { ReconciliationResponse, DataQualityResponse } from "./objects";
import { SafetyCheck, Severity } from "./objects";

export const mockReconciliationResponses: ReconciliationResponse[] = [
  {
    patient_context: {
      age: 68,
      conditions: ["Hypertension", "Type 2 Diabetes", "Hyperlipidemia"],
      recent_labs: {
        HbA1c: "7.2%",
        LDL: "95 mg/dL",
        blood_pressure: "138/82 mmHg",
        creatinine: "1.1 mg/dL"
      }
    },
    reconciled_medication: "Metformin 1000mg twice daily",
    confidence_score: 0.92,
    reasoning: "Hospital EHR shows most recent update (March 15) with dose increase from 500mg to 1000mg. Patient self-report confirms 1000mg BID with matching fill date. Outpatient record is older (February 20) and reflects previous lower dose.",
    recommended_actions: [
      "Confirm dose change timing with patient",
      "Verify prescribing provider ordered increase",
      "Update all systems to reflect current 1000mg BID dosing"
    ],
    clinical_safety_check: SafetyCheck.Passed
  },
  {
    patient_context: {
      age: 55,
      conditions: ["Chronic Heart Failure", "Atrial Fibrillation"],
      recent_labs: {
        INR: "2.3",
        potassium: "4.2 mEq/L",
        BNP: "450 pg/mL",
        ejection_fraction: "35%"
      }
    },
    reconciled_medication: "Warfarin 5mg daily",
    confidence_score: 0.55,
    reasoning: "Critical conflict detected: Cardiology prescribes Warfarin 5mg daily (most recent, March 18) while Primary Care has Apixaban 5mg BID (March 10). Patient is on anticoagulation but unclear which agent. Both sources are highly reliable. INR of 2.3 suggests patient is taking Warfarin.",
    recommended_actions: [
      "URGENT: Contact prescribing cardiologist immediately",
      "Verify which anticoagulant patient is actually taking",
      "Discontinue incorrect medication",
      "Check for potential drug interactions or adverse events",
      "Update medication reconciliation across all systems"
    ],
    clinical_safety_check: SafetyCheck.Flagged
  },
  {
    patient_context: {
      age: 72,
      conditions: ["Chronic Kidney Disease Stage 3", "Hypertension"],
      recent_labs: {
        creatinine: "1.6 mg/dL",
        eGFR: "44 mL/min/1.73m²",
        potassium: "4.8 mEq/L"
      }
    },
    reconciled_medication: "Lisinopril 10mg once daily",
    confidence_score: 0.98,
    reasoning: "All three sources (Hospital EHR, Primary Care, Pharmacy) agree on Lisinopril 10mg daily with identical recent update dates. Dose is appropriate for renal function (eGFR 44).",
    recommended_actions: [
      "Continue current medication",
      "Monitor renal function and potassium quarterly"
    ],
    clinical_safety_check: SafetyCheck.Passed
  }
];

export const mockDataQualityResponses: DataQualityResponse[] = [
  {
    demographics: {
      name: "Sarah Johnson",
      dob: "1975-06-12",
      gender: "Female"
    },
    overall_score: 94,
    breakdown: {
      completeness: 98,
      accuracy: 95,
      timeliness: 92,
      clinical_plausibility: 91
    },
    issues_detected: [
      {
        field: "vital_signs.blood_pressure",
        issue: "Blood pressure slightly elevated (128/78) - within acceptable range but may warrant monitoring",
        severity: Severity.Low
      }
    ]
  },
  {
    demographics: {
      name: "John Doe",
      dob: "",
      gender: "M"
    },
    overall_score: 42,
    breakdown: {
      completeness: 45,
      accuracy: 38,
      timeliness: 35,
      clinical_plausibility: 50
    },
    issues_detected: [
      {
        field: "demographics.dob",
        issue: "Date of birth is missing - required for patient identification and age-based clinical decisions",
        severity: Severity.High
      },
      {
        field: "medications",
        issue: "Medication names are vague ('aspirin', 'some blood pressure med') - need specific names, doses, and frequencies",
        severity: Severity.High
      },
      {
        field: "conditions",
        issue: "Conditions use abbreviations (HTN, DM) without full names - should use standardized terminology",
        severity: Severity.Medium
      },
      {
        field: "vital_signs",
        issue: "Critical vital signs detected: BP 180/110 (hypertensive crisis), HR 145 (tachycardia), Temp 103.2°F (fever) - requires immediate clinical attention",
        severity: Severity.High
      },
      {
        field: "last_updated",
        issue: "Data is 7+ months old (August 2023) - may not reflect current patient status",
        severity: Severity.High
      },
      {
        field: "allergies",
        issue: "No allergies documented - verify if truly no allergies or if data is missing",
        severity: Severity.Medium
      }
    ]
  },
  {
    demographics: {
      name: "Maria Garcia",
      dob: "1960-03-22",
      gender: "Female"
    },
    overall_score: 88,
    breakdown: {
      completeness: 90,
      accuracy: 92,
      timeliness: 85,
      clinical_plausibility: 85
    },
    issues_detected: [
      {
        field: "medications",
        issue: "Missing frequency for one medication - should specify dosing schedule",
        severity: Severity.Medium
      },
      {
        field: "last_updated",
        issue: "Data is 2 months old - consider updating for active patients",
        severity: Severity.Low
      }
    ]
  }
];
