import { useState } from "react"; 
import { DataQualityPage } from "./pages/DataQualityPage";
import { ReconcilePage } from "./pages/ReconcilePage";

export default function App() {
  const [tab, setTab] = useState<"reconcile" | "quality">("reconcile");

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: 24 }}>
      <h1>Clinical Data Reconciliation Engine</h1>

      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        <button onClick={() => setTab("reconcile")}>Medication Reconciliation</button>
        <button onClick={() => setTab("quality")}>Data Quality Validation</button>
      </div>

      {tab === "reconcile" ? <ReconcilePage /> : <DataQualityPage />}
    </div>
  );
}