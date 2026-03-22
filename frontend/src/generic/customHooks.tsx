import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { DataQualityResponse, ReconciliationResponse, ReviewStatus } from "./objects";

type ReturnContextType = {
  reconciliations: ReconciliationResponse[],
  dataQualities: DataQualityResponse[],
  updateReconciliations: (newReconciliation: ReconciliationResponse) => boolean,
  updateDataQualities: (newDataQuality: DataQualityResponse) => boolean,
  updateReconciliationStatus: (index: number, status: ReviewStatus) => void,
  updateDataQualityStatus: (index: number, status: ReviewStatus) => void,
  isSubmitting: boolean,
  setIsSubmitting: (value: boolean) => void
}

const ReturnContext = createContext<ReturnContextType | undefined>(undefined);

export function useReturns(): ReturnContextType {
  const context = useContext(ReturnContext);

  // Should never happen
  if (!context) {
    throw new Error("useReturns must be used within a ReturnProvider");
  }

  return context;
}

export function ReturnProvider({ ...props }) {
  const [reconciliations, setReconciliations] = useState<ReconciliationResponse[]>([]);
  const [dataQualities, setDataQualities] = useState<DataQualityResponse[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const updateReconciliations = useCallback((newReconciliation: ReconciliationResponse): boolean => {
    // Check for duplicates against current state
    const currentRecs = reconciliations;
    const isDuplicate = currentRecs.some(rec =>
      rec.reconciled_medication === newReconciliation.reconciled_medication &&
      rec.confidence_score === newReconciliation.confidence_score &&
      rec.reasoning === newReconciliation.reasoning
    );

    if (!isDuplicate) {
      setReconciliations(recs => [{ ...newReconciliation, status: "pending" }, ...recs]);
    }

    return isDuplicate;
  },[reconciliations]);

  const updateDataQualities = useCallback((newDataQuality: DataQualityResponse): boolean => {
    // Check for duplicates against current state
    const currentDqs = dataQualities;
    const isDuplicate = currentDqs.some(dq =>
      dq.overall_score === newDataQuality.overall_score &&
      dq.breakdown.completeness === newDataQuality.breakdown.completeness &&
      dq.breakdown.accuracy === newDataQuality.breakdown.accuracy &&
      dq.breakdown.timeliness === newDataQuality.breakdown.timeliness &&
      dq.breakdown.clinical_plausibility === newDataQuality.breakdown.clinical_plausibility
    );

    if (!isDuplicate) {
      setDataQualities(dqs => [{ ...newDataQuality, status: "pending" }, ...dqs]);
    }

    return isDuplicate;
  },[dataQualities]);

  const updateReconciliationStatus = useCallback((index: number, status: ReviewStatus) => {
    setReconciliations(recs => recs.map((rec, i) => i === index ? { ...rec, status } : rec))
  },[]);

  const updateDataQualityStatus = useCallback((index: number, status: ReviewStatus) => {
    setDataQualities(dqs => dqs.map((dq, i) => i === index ? { ...dq, status } : dq))
  },[]);

  const ctx = useMemo<ReturnContextType>(() => ({
    reconciliations,
    dataQualities,
    updateReconciliations,
    updateDataQualities,
    updateReconciliationStatus,
    updateDataQualityStatus,
    isSubmitting,
    setIsSubmitting
  }), [reconciliations, dataQualities, updateReconciliations, updateDataQualities, updateReconciliationStatus, updateDataQualityStatus, isSubmitting])

  return <ReturnContext.Provider value={ctx} {...props}/>
}