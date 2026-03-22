export enum Tab {
  Reconciliation = 0,
  DataQuality
}

export const TabConfig = {
  [Tab.Reconciliation]: {
    key: "reconcile",
    label: "Medication Reconciliation",
    emptyMessage: "No recent reconciliation records",
    emptyHint: "Upload patient medication data to begin reconciliation"
  },
  [Tab.DataQuality]: {
    key: "quality",
    label: "Data Quality Validation",
    emptyMessage: "No recent validation records",
    emptyHint: "Upload clinical data to assess quality metrics"
  }
} as const;

export type TabKey = typeof TabConfig[Tab]["key"];
