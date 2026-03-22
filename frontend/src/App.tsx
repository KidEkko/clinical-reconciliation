import { useCallback, useState } from "react";

import { DataQualityCard, EmptyState, ReconciliationCard } from "./components/cards";
import { DataQualitySkeleton, ReconciliationSkeleton } from "./components/skeletons";
import TabNav from "./components/TabNav";
import { Button } from "./components/ui/button";
import JsonUpload from "./components/upload";
import { useReturns } from "./generic/customHooks";
import { mockDataQualityResponses, mockReconciliationResponses } from "./generic/mockData";
import { Tab, TabConfig } from "./generic/tabs";

import "@/App.css";

export default function App() {
  const [tab, setTab] = useState<Tab>(Tab.Reconciliation); 
  const { reconciliations, dataQualities, updateReconciliations, updateDataQualities, updateReconciliationStatus, updateDataQualityStatus, isSubmitting } = useReturns();

  const showDevTools = import.meta.env.VITE_SHOW_DEV_TOOLS === 'true';

  const tabs = [
    { label: TabConfig[Tab.Reconciliation].label, value: Tab.Reconciliation },
    { label: TabConfig[Tab.DataQuality].label, value: Tab.DataQuality },
  ];

  const handleTabChange = useCallback((tabValue: number) => {
    if (isSubmitting) return;
    
    setTab(tabValue);
  }, [isSubmitting]);

  const loadExampleData = useCallback(() => {
    mockReconciliationResponses.forEach(mock => {
      updateReconciliations(mock);
    });
    mockDataQualityResponses.forEach(mock => {
      updateDataQualities(mock);
    });
  }, [tab, updateReconciliations, updateDataQualities]);

  const reconciliationMap = useCallback(() => {
    if (reconciliations.length === 0 && !isSubmitting) {
      return <EmptyState config={TabConfig[Tab.Reconciliation]} />
    }
    return (
      <div className="flex flex-col gap-4 py-10">
        {isSubmitting && (
          <ReconciliationSkeleton key="loading" />
        )}
        {reconciliations.map((reconciliation, index) => (
          <ReconciliationCard
            key={index}
            data={reconciliation}
            onAccept={() => updateReconciliationStatus(index, "accepted")}
            onReject={() => updateReconciliationStatus(index, "rejected")}
          />
        ))}
      </div>
    )
  }, [reconciliations, updateReconciliationStatus, isSubmitting, tab])

  const dataQualitiesMap = useCallback(() => {
    if (dataQualities.length === 0 && !isSubmitting) {
      return <EmptyState config={TabConfig[Tab.DataQuality]} />
    }
    return (
      <div className="flex flex-col gap-4 py-10">
        {isSubmitting && (
          <DataQualitySkeleton key="loading" />
        )}
        {dataQualities.map((dataQuality, index) => (
          <DataQualityCard
            key={index}
            data={dataQuality}
            onAccept={() => updateDataQualityStatus(index, "accepted")}
            onReject={() => updateDataQualityStatus(index, "rejected")}
          />
        ))}
      </div>
    )
  }, [dataQualities, updateDataQualityStatus, isSubmitting, tab])

  return (
    <div className="max-w-7xl lg:min-w-7xl bg-background min-h-screen mx-auto pt-8 lg:pt-16 border-x border-border">
      <div className="flex items-center justify-between mb-8 px-4 lg:px-8">
        <h1 className="text-left text-3xl font-semibold tracking-tight text-destructive">Clinical Data Reconciliation</h1>
        {showDevTools && (
          <Button
            onClick={loadExampleData}
            variant="outline"
            size="sm"
            className="shadow-lift"
          >
            Load Example Data
          </Button>
        )}
      </div>

      <div className="w-full mx-auto">
        <div className="border-b-2 border-border px-4 lg:px-8">
          <TabNav
            tabs={tabs}
            activeTab={tab}
            onTabChange={handleTabChange}
            disabled={isSubmitting}
          />
        </div>

        <div className="flex flex-col lg:flex-row gap-6 px-4 lg:px-8">
          <div className="w-full lg:w-auto lg:max-w-100 lg:border-r border-border pr-0 lg:pr-6 lg:min-h-[calc(100vh-11rem)]">
            <div className="lg:sticky lg:top-6">
              <JsonUpload tab={tab}/>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            {
              TabConfig[tab].key === "reconcile" ?
                reconciliationMap()
                :
                dataQualitiesMap()
            }
          </div>
        </div>
      </div>
    </div>
  );
}
