import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { DataQualityResponse, ReconciliationResponse } from "./objects";

export function useLoading(onByDefault: boolean) {
  const [loading, setLoading] = useState<boolean>(!!onByDefault);

  function startLoading() {
    setLoading(true);
  }

  function stopLoading() {
    setLoading(false);
  }

  return { loading, startLoading, stopLoading };
}

type ReturnContextType = {
  reconciliations: ReconciliationResponse[],
  dataQualities: DataQualityResponse[]
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
  
  const updateReconciliations = useCallback((newReconciliation: ReconciliationResponse) => {
    setReconciliations(recs => [...reconciliations, newReconciliation])
  },[reconciliations]);

  const updateDataQualities = useCallback((newDataQuality: DataQualityResponse) => {
    setDataQualities(dqs => [... dataQualities, newDataQuality])
  },[dataQualities]);

  const ctx = useMemo<ReturnContextType>(() => ({reconciliations, dataQualities, updateReconciliations, updateDataQualities}),
  [reconciliations, dataQualities, updateReconciliations, updateDataQualities])

  return <ReturnContext.Provider value={ctx} {...props}/>
}