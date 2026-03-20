enum Reliability {
  High = "High",
  Medium = "Medium",
  Low = "Low"
}

enum Severity {
  High = "High",
  Medium = "Medium",
  Low = "Low"
}

export const SeverityMap = new Map([
  [Severity.High, "red"],
  [Severity.Medium, "yellow"],
  [Severity.Low, "green"]
])

enum SafetyCheck {
  Passed = "Passed",
  Flagged = "Flagged",
  Review = "Requires Review"
}

export class ApiResponse<T> {
  constructor(private response: Response) {}

  async json(): Promise<T> {
    return (await this.response.json()) as T;
  }

  get ok() {
    return this.response.ok;
  }

  get status() {
    return this.response.status;
  }
}

export type ReconciliationResponse = {
  patient_context: PatientContext,
  reconciled_medication: string,
  confidence_score: number,
  reasoning: string,
  recommended_actions: string[],
  clinical_safety_check: SafetyCheck
}


export type ReconciliationRequest = {
  patient_context: PatientContext,
  sources: Source[],
}

type PatientContext = {
  age: number,
  conditions: string[],
  recent_labs: Map<string, any>,
}

type Source = {
  system: string,
  medication: string,
  last_updated: string,
  last_filled: string,
  source_reliability: Reliability,
}

export type DataQualityResponse = {
  demographics: Demographics,
  overall_score: number,
  breakdown: Breakdown,
  issues_detected: DataQualityIssue[],
}

type Breakdown = {
  completeness: number,
  accuracy: number,
  timeliness: number,
  clinical_plausability: number,
}

type DataQualityIssue = {
  field: string,
  issue: string,
  severity: Severity,
}

export type DataQualityRequest = {
  demographics: Demographics,
  medications: string[],
  allergies: string[],
  conditions: string[],
  vital_signs: Map<string, any>,
  last_updated: string,
}

type Demographics = {
  name: string,
  dob: string,
  gender: string
}