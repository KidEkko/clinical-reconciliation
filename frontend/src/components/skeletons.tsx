import { Skeleton } from "./ui/skeleton";

export function ReconciliationSkeleton() {
  return (
    <div className="panel-surface shadow-lift flex w-full flex-col gap-4 p-6 lg:p-8 mx-2">
      <div className="flex items-center justify-between rounded-xl border border-border bg-muted/60 p-3">
        <Skeleton className="h-5 w-32" />
        <div className="flex space-x-2">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-20" />
        </div>
      </div>
      <div className="flex items-center justify-between rounded-xl border border-border bg-card/60 p-3">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-6 w-28 rounded-full" />
      </div>
      <div className="grid gap-4 rounded-xl border border-border bg-card/50 p-4 lg:grid-cols-2">
        <div className="flex flex-col space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
        <div className="flex flex-col space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>
      </div>
    </div>
  );
}

export function DataQualitySkeleton() {
  return (
    <div className="panel-surface shadow-lift flex w-full flex-col gap-4 p-6 lg:p-8 mx-2">
      <div className="flex items-center justify-between rounded-xl border border-border bg-muted/60 p-3">
        <Skeleton className="h-5 w-40" />
        <div className="flex space-x-2">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-20" />
        </div>
      </div>

      <div className="rounded-xl border border-border bg-muted/50 p-4 space-y-3">
        <div className="flex items-center justify-between rounded-lg border border-border/70 bg-card/60 px-3 py-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-6 w-12 rounded-full" />
        </div>
        <div className="grid gap-3 lg:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="flex items-center justify-between rounded-lg border border-border/70 bg-card/60 px-3 py-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-6 w-12 rounded-full" />
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-border bg-card/50 p-4">
        <Skeleton className="h-4 w-28 mb-3" />
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/40 p-3">
              <div className="space-y-1 pr-3 flex-1">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-full" />
              </div>
              <Skeleton className="h-6 w-16 rounded-full shrink-0" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
