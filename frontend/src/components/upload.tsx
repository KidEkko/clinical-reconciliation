import { type ReconciliationRequest, type DataQualityRequest } from "@/generic/objects";
import { AssessDataQuality, ReconcileMedication } from "@/generic/requests";
import { useState } from "react";
import { Button } from "./ui/button";

type UploadProps = {
  tab: number,

}

export default function JsonUpload({tab}: UploadProps) {
  const [error, setError] = useState("");
  const [parsedData, setParsedData] = useState<ReconciliationRequest | DataQualityRequest | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    setError("");
    setParsedData(null);

    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const json = JSON.parse(text);
      
      if (tab === 0) {
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
      if (tab === 0) {
        resp = await ReconcileMedication(parsedData as ReconciliationRequest);
      } else {
        resp = await AssessDataQuality(parsedData as DataQualityRequest);
      }

    } catch {
      setError("Failed to send request.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <>
    <div className="flex mx-4 lg:mx-8">
      <div className="mx-auto max-w-xl rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-900">Upload JSON Request</h2>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700">JSON file</label>
          <input
            type="file"
            accept=".json,application/json"
            onChange={handleFileChange}
            className="mt-2 cursor-pointer  block w-full rounded-lg border border-gray-300 p-2 text-sm file:mr-4 file:rounded-md file:border-0 file:bg-gray-100 file:px-3 file:py-2 file:text-sm file:font-medium hover:file:bg-gray-200"
          />
        </div>


        {error && (
          <div className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        )}

        <Button
          onClick={handleSubmit}
          disabled={!parsedData || isSubmitting}
          className="mt-5 inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
        >
          {isSubmitting ? "Sending..." : "Send Request"}
        </Button>
      </div>
    </div>
    </>
    
  );
}