import React, { useCallback, useState } from "react"; 
import { Button } from "./components/ui/button";
import "@/App.css"
import { useLoading, useReturns } from "./generic/customHooks";
import JsonUpload from "./components/upload";
import { DataQualityCard, ReconciliationCard, Skeletons } from "./components/cards";

// Overcomplicated for this basic of a project, but what I'm used to.
enum Tab {
  Reconciliation = 0,
  DataQuality
}

const TabMap = new Map([
  [Tab.Reconciliation, "reconcile"],
  [Tab.DataQuality, "quality"]
])

/**
 * submit functions for both types
 * components for uploading files and displaying data
 * display data component look:
 * card. rounded border with light shadow style.
 * red/yellow/green color scheme somewhere. could be a small circle next to the confidence score in the upper right.. actually yes that
 * patient name in top left. "John Doe" by default if not provided for data quality. --- ask maybe?
 * actually nah, default john doe, unknown DOB and gender
 * reasoning and recommended actions
 * 0-50 red, 51-75 yellow, up green
 * accept/reject buttons on top right. edit button replaces both on accept, resend option if reject. Initial version will just call it again, ideally use a different prompt or smth?
 * save patient contexts to response objects to enable saving and searching.
 * pagination for things: issues, recommended actions, cards in general.
 * 
 * save some kind of ID for each request? probably ideal for a real practice
 * 
 * 
 */

export default function App() {
  const [tab, setTab] = useState<Tab>(0);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const { loading, startLoading, stopLoading } = useLoading(false);
  const { reconciliations, dataQualities } = useReturns();

  const swapTab = useCallback((tabToSwapTo: Tab) => (e: React.MouseEvent<HTMLButtonElement>) => {
    if (submitting || loading) {
      return;
    }
    // reset any/all forms
    setTab(tabToSwapTo);
  }, [submitting, loading]);

  const reconciliationMap = useCallback(() => {
    if (reconciliations.length === 0) {
      return <Skeletons />
    }
    return reconciliations.map((reconciliation) => (<ReconciliationCard data={reconciliation} />))
  }, [reconciliations])

  const dataQualitiesMap = useCallback(() => {
    if (dataQualities.length === 0) {
      return <Skeletons />
    }
    return dataQualities.map((dataQuality) => (<DataQualityCard data={dataQuality} />))
  }, [reconciliations])

  return (
    <body className="max-w-7xl bg-inherit h-full mx-auto py-12 lg:py-24 border-x border-white dark:border-black">
      <h1>Data Reconciliation</h1>
      <div className="w-full mx-auto  border-t border-black">

        <div className="flex mb-24 px-6 lg:px-12 space-x-2">
          <Button className="bShad rounded-2xl border border-black " 
            disabled={loading} 
            onClick={swapTab(Tab.Reconciliation)}
          >
            Medication Reconciliation
          </Button>
          <Button className="bShad rounded-2xl border border-black" 
            disabled={loading} 
            onClick={swapTab(Tab.DataQuality)}
          >
            Data Quality Validation
          </Button>
        </div>
        {reconciliations.map((rec) => (<><div>rec.medication</div></>))}

        <div className="flex lg:flex-row justify-center">
          <div className="flex h-full my-auto border-r dark:border-black border-amber-300 self-start">
            <JsonUpload tab={tab}/>
          </div>
            {
              TabMap.get(tab) === "reconcile" ? 
                reconciliationMap() : 
                dataQualitiesMap()
            }
        </div>
      </div>
    </body>
  );
}
