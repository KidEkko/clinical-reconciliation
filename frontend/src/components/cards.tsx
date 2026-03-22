import type { DataQualityResponse, ReconciliationResponse, ReviewStatus } from "@/generic/objects";
import { Severity } from "@/generic/objects";

import { Button } from "./ui/button";

type ReconciliationCardProps = {
  data: ReconciliationResponse;
  onAccept: () => void;
  onReject: () => void;
}

type ScoreTone = "high" | "medium" | "low";

const scoreTonePills: Record<ScoreTone, string> = {
  high: "bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200",
  medium: "bg-amber-50 text-amber-800 dark:bg-amber-900/30 dark:text-amber-200",
  low: "bg-rose-50 text-rose-800 dark:bg-rose-900/30 dark:text-rose-200",
};

const severityPills: Record<Severity, string> = {
  [Severity.High]: "bg-rose-50 text-rose-800 dark:bg-rose-900/40 dark:text-rose-200",
  [Severity.Medium]: "bg-amber-50 text-amber-800 dark:bg-amber-900/30 dark:text-amber-200",
  [Severity.Low]: "bg-emerald-50 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200",
};

function getScoreTone(score: number): ScoreTone {
  if (score > 75) return "high";
  if (score > 50) return "medium";
  return "low";
}

const statusBadge: Record<ReviewStatus, { text: string; className: string }> = {
  pending: { text: "Pending Review", className: "bg-muted text-muted-foreground" },
  accepted: { text: "Accepted", className: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200" },
  rejected: { text: "Rejected", className: "bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-200" }
};

const cardBackground: Record<ReviewStatus, string> = {
  pending: "",
  accepted: "bg-emerald-50/50 dark:bg-emerald-950/20",
  rejected: "bg-rose-50/50 dark:bg-rose-950/20"
};

type SafetyCheck = "PASSED" | "FLAGGED" | "REQUIRES_REVIEW";

const safetyCheckBadge: Record<SafetyCheck, { text: string; className: string; icon: string }> = {
  PASSED: {
    text: "Safe",
    className: "bg-emerald-50 text-emerald-800 border border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-200 dark:border-emerald-800",
    icon: "✓"
  },
  FLAGGED: {
    text: "Safety Alert",
    className: "bg-rose-50 text-rose-800 border border-rose-200 dark:bg-rose-900/40 dark:text-rose-200 dark:border-rose-800",
    icon: "⚠"
  },
  REQUIRES_REVIEW: {
    text: "Review Required",
    className: "bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-900/30 dark:text-amber-200 dark:border-amber-800",
    icon: "⚡"
  }
};

// Map technical field names to human-readable names
function formatFieldName(field: string): string {
  const fieldMap: Record<string, string> = {
    "demographics.dob": "Date of Birth",
    "demographics.name": "Patient Name",
    "demographics.gender": "Gender",
    "vital_signs": "Vital Signs",
    "vital_signs.blood_pressure": "Blood Pressure",
    "vital_signs.heart_rate": "Heart Rate",
    "vital_signs.temperature": "Temperature",
    "vital_signs.respiratory_rate": "Respiratory Rate",
    "vital_signs.oxygen_saturation": "Oxygen Saturation",
    "medications": "Medications",
    "allergies": "Allergies",
    "conditions": "Conditions",
    "last_updated": "Last Updated",
  };

  return fieldMap[field] || field
    .split(".")
    .pop()!
    .split("_")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

export function ReconciliationCard({ data, onAccept, onReject }: ReconciliationCardProps) {
  const confidenceTone = getScoreTone(data.confidence_score);
  const status = data.status || "pending";
  const badge = statusBadge[status];
  const safetyBadge = safetyCheckBadge[data.clinical_safety_check as SafetyCheck];

  return (
    <>
      <div className={`panel-surface shadow-lift flex w-full flex-col gap-4 p-6 lg:p-8 mx-2 ${cardBackground[status]}`}>
        <div className="flex items-center justify-between rounded-xl border border-border bg-muted/60 p-3">
          <p className="text-sm font-semibold text-foreground">Patient: John Doe</p>
          <div className="flex space-x-2">
            {status === "pending" ? (
              <>
                <Button className="shadow-lift" size="sm" onClick={onAccept}>Accept</Button>
                <Button className="shadow-lift" size="sm" variant="destructive" onClick={onReject}>Reject</Button>
              </>
            ) : (
              <span className={`pill ${badge.className}`}>{badge.text}</span>
            )}
          </div>
        </div>
        <div className="flex items-center justify-between rounded-xl border border-border bg-card/60 p-3">
          <div className="flex-1">
            <div className="lg:text-lg font-semibold text-foreground">{data.reconciled_medication}</div>
          </div>
          <div className="flex items-center gap-2 ml-4">
            <span className={`pill ${safetyBadge.className} flex items-center gap-1.5`}>
              <span className="text-base">{safetyBadge.icon}</span>
              <span className="hidden sm:inline">{safetyBadge.text}</span>
            </span>
            <span className={`pill ${scoreTonePills[confidenceTone]}`}>
              Confidence {data.confidence_score}
            </span>
          </div>
        </div>
        <div className="grid gap-4 rounded-xl border border-border bg-card/50 p-4 lg:grid-cols-2">
          <div className="flex flex-col space-y-2">
            <div className="text-sm font-semibold text-muted-foreground">Reasoning</div>
            <div className="text-sm text-left leading-relaxed">{data.reasoning}</div>
          </div>
          <div className="flex flex-col space-y-2">
            <div className="text-sm font-semibold text-muted-foreground">Recommended Actions</div>
            <ul className="list-disc space-y-1 pl-4 text-left text-sm leading-relaxed">
              {data.recommended_actions?.length ? data.recommended_actions.map((action, index) => (
                <li key={`${action}-${index}`}>
                  {action}
                </li>
              )) : (
                <li>No actions provided.</li>
              )}
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}

type DataQualityCardProps = {
  data: DataQualityResponse;
  onAccept: () => void;
  onReject: () => void;
}

export function DataQualityCard({ data, onAccept, onReject }: DataQualityCardProps) {
  const overallTone = getScoreTone(data.overall_score);
  const status = data.status || "pending";
  const badge = statusBadge[status];
  const breakdownEntries = [
    { label: "Completeness", value: data.breakdown.completeness },
    { label: "Accuracy", value: data.breakdown.accuracy },
    { label: "Timeliness", value: data.breakdown.timeliness },
    { label: "Clinical Plausibility", value: data.breakdown.clinical_plausibility },
  ];

  return (
    <>
      <div className={`panel-surface shadow-lift flex w-full flex-col gap-4 p-6 lg:p-8 mx-2 ${cardBackground[status]}`}>
        <div className="flex items-center justify-between rounded-xl border border-border bg-muted/60 p-3">
          <p className="text-sm font-semibold text-foreground">Patient: {data.demographics.name}</p>
          <div className="flex space-x-2">
            {status === "pending" ? (
              <>
                <Button className="shadow-lift" size="sm" onClick={onAccept}>Accept</Button>
                <Button className="shadow-lift" size="sm" variant="destructive" onClick={onReject}>Reject</Button>
              </>
            ) : (
              <span className={`pill ${badge.className}`}>{badge.text}</span>
            )}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-muted/50 p-4 space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-border/70 bg-card/60 px-3 py-2">
            <span className="text-sm font-medium text-foreground">Overall Score</span>
            <span className={`pill ${scoreTonePills[overallTone]}`}>{data.overall_score}</span>
          </div>
          <div className="grid gap-3 lg:grid-cols-2">
            {breakdownEntries.map(({ label, value }) => {
              const tone = getScoreTone(value);
              return (
                <div
                  key={label}
                  className="flex items-center justify-between rounded-lg border border-border/70 bg-card/60 px-3 py-2"
                >
                  <span className="text-sm font-medium text-foreground">{label}</span>
                  <span className={`pill ${scoreTonePills[tone]}`}>{value}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card/50 p-4">
          <div className="text-sm font-semibold text-muted-foreground mb-3">Issues Detected</div>
          <div className="space-y-3">
            {data.issues_detected.map((issue, index) => (
              <div
                key={`${issue.field}-${index}`}
                className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/40 p-3"
              >
                <div className="space-y-1 pr-3 flex-1">
                  <div className="text-sm font-semibold text-foreground">{formatFieldName(issue.field)}</div>
                  <div className="text-sm text-muted-foreground leading-relaxed">{issue.issue}</div>
                </div>
                <span className={`pill ${severityPills[issue.severity]} shrink-0`}>
                  {issue.severity === Severity.High ? "High" : issue.severity === Severity.Medium ? "Medium" : "Low"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
}

type EmptyStateProps = {
  config: {
    emptyMessage: string;
    emptyHint: string;
  };
};

export function EmptyState({ config }: EmptyStateProps) {
  return (
    <div className="w-full m-auto lg:mx-8 flex items-center justify-center py-10">
      <div className="text-center space-y-3 py-12">
        <div className="text-lg font-medium text-muted-foreground">{config.emptyMessage}</div>
        <div className="text-sm text-muted-foreground/70">{config.emptyHint}</div>
      </div>
    </div>
  )
}
