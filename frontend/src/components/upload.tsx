import { useState } from "react";
import { toast } from "sonner";

import type { DataQualityRequest, DataQualityResponse, ReconciliationRequest, ReconciliationResponse } from "@/generic/objects";
import { useReturns } from "@/generic/customHooks";
import { AssessDataQuality, ReconcileMedication } from "@/generic/requests";
import { Tab, TabConfig } from "@/generic/tabs";

import { Button } from "./ui/button";

type UploadProps = {
  tab: Tab,

}

export default function JsonUpload({tab}: UploadProps) {
  const [error, setError] = useState("");
  const [parsedData, setParsedData] = useState<ReconciliationRequest | DataQualityRequest | null>(null);
  const { updateReconciliations, updateDataQualities, isSubmitting, setIsSubmitting } = useReturns();

  const config = TabConfig[tab];

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    setParsedData(null);

    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const json = JSON.parse(text);
      
      if (tab === Tab.Reconciliation) {
        setParsedData(json as ReconciliationRequest);
      } else {
        setParsedData(json as DataQualityRequest)
      }
    } catch {
      setError("Could not read or parse the JSON file.");
    }
  };

  async function handleSubmit() {
    if (!parsedData) {
      setError("Upload a valid JSON file before submitting.");
      return;
    }

    setError("");
    setIsSubmitting(true);

    try {
      let resp;
      let isDuplicate = false;

      if (tab === Tab.Reconciliation) {
        const data = parsedData as ReconciliationRequest
        resp = await ReconcileMedication(data) as ReconciliationResponse;
        resp.patient_context = data.patient_context
        isDuplicate = updateReconciliations(resp);
      } else {
        const data = parsedData as DataQualityRequest
        resp = await AssessDataQuality(data) as DataQualityResponse;
        resp.demographics = data.demographics
        isDuplicate = updateDataQualities(resp);
      }

      if (isDuplicate) {
        await new Promise(resolve => setTimeout(resolve, 1000));

        toast.info("Duplicate Request", {
          description: "This request was already processed and returned from cache."
        });
      }

    } catch {
      setError("Failed to send request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full panel-surface p-6 mt-10">
      <h2 className="text-xl font-semibold text-destructive mb-1">{config.label}</h2>
      <div className="mt-2">
          <label className="block text-sm font-medium text-muted-foreground">JSON file</label>
          <input
            type="file"
            accept=".json,application/json"
            onChange={handleFileChange}
            className="mt-2 block w-full cursor-pointer rounded-lg border border-border bg-background/60 p-2 text-sm text-foreground file:mr-4 file:rounded-md file:border-0 file:bg-muted/80 file:px-3 file:py-2 file:text-sm file:font-medium file:text-foreground hover:file:bg-muted"
          />
        </div>


        {error && (
          <div className="mt-4 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </div>
        )}

      <Button
        onClick={handleSubmit}
        disabled={!parsedData || isSubmitting}
        className="mt-5 shadow-lift disabled:cursor-not-allowed"
      >
        {isSubmitting ? "Sending..." : "Send Request"}
      </Button>
    </div>
  );
}
