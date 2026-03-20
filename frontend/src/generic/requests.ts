import { ApiResponse, type DataQualityRequest, type DataQualityResponse, type ReconciliationRequest, type ReconciliationResponse } from "./objects";

// Not sure what this type of system looks like in a professional environment, or if it is even desirable
const PubRequests = Object.freeze({
  Reconciliation: "reconcile/medication",
  DataQuality: "validate/data-quality",
})

function getAPICall(reqType: string) {
  return `${window.location.origin}/api/${reqType}`;
}

export async function GenericFetch<T>(type: string, request?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(getAPICall(type), request);
  return new ApiResponse<T>(response);
}

export async function ReconcileMedication(req: ReconciliationRequest): Promise<ReconciliationResponse | Error> {
  try {
    const resp = await GenericFetch(PubRequests.Reconciliation, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    })

    return (await resp.json()) as ReconciliationResponse;
  } catch (err) {
      return new Error("Failed to reconcile medication: " + err );
  }
}

// TODO: FIX ERROR MESSAGES
export async function AssessDataQuality(req: DataQualityRequest): Promise<DataQualityResponse | Error> {
  try {
    const resp = await GenericFetch(PubRequests.DataQuality, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    })

    return (await resp.json()) as DataQualityResponse;
  } catch (err) {
      return new Error("Failed to assess data quality: " + err );
  }
}