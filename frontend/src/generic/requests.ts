import type { DataQualityRequest, DataQualityResponse, ReconciliationRequest, ReconciliationResponse } from "./objects";
import { ApiResponse } from "./objects";
import { hashApiKey } from "./crypto";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const API_ENDPOINTS = Object.freeze({
  Reconciliation: "/api/reconcile/medication",
  DataQuality: "/api/validate/data-quality",
});

function getAPIUrl(endpoint: string): string {
  return `${API_BASE_URL}${endpoint}`;
}

function getRequestHeaders(): HeadersInit {
  const apiKey = import.meta.env.VITE_APP_API_KEY || "";
  const hashedApiKey = hashApiKey(apiKey);

  return {
    "Content-Type": "application/json",
    "X-API-Key": hashedApiKey,
  };
}

export async function GenericFetch<T>(endpoint: string, request?: RequestInit): Promise<ApiResponse<T>> {
  const response = await fetch(getAPIUrl(endpoint), request);
  return new ApiResponse<T>(response);
}

async function handleResponse<T>(resp: ApiResponse<T>): Promise<T> {
  if (!resp.ok) {
    if (resp.status === 401) {
      throw new Error("Authentication failed. Please check your API key.");
    } else if (resp.status === 503) {
      throw new Error("Service temporarily unavailable. The API may be rate limited. Please try again later.");
    } else if (resp.status === 502) {
      throw new Error("External service error. The LLM service may be unavailable.");
    } else if (resp.status === 422) {
      throw new Error("Invalid request data. Please check your input.");
    } else {
      throw new Error(`Request failed with status ${resp.status}`);
    }
  }

  return await resp.json();
}

export async function ReconcileMedication(req: ReconciliationRequest): Promise<ReconciliationResponse> {
  try {
    const resp = await GenericFetch<ReconciliationResponse>(API_ENDPOINTS.Reconciliation, {
      method: "POST",
      headers: getRequestHeaders(),
      body: JSON.stringify(req),
    });

    return await handleResponse(resp);
  } catch (err) {
    if (err instanceof Error) {
      throw err;
    }
    throw new Error("Failed to reconcile medication: " + String(err));
  }
}

export async function AssessDataQuality(req: DataQualityRequest): Promise<DataQualityResponse> {
  try {
    const resp = await GenericFetch<DataQualityResponse>(API_ENDPOINTS.DataQuality, {
      method: "POST",
      headers: getRequestHeaders(),
      body: JSON.stringify(req),
    });

    return await handleResponse(resp);
  } catch (err) {
    if (err instanceof Error) {
      throw err;
    }
    throw new Error("Failed to assess data quality: " + String(err));
  }
}