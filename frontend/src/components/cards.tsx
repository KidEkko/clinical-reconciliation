import { SeverityMap, type DataQualityResponse, type ReconciliationResponse } from "@/generic/objects";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader } from "./ui/card";
import { Skeleton } from "./ui/skeleton";

type ReconciliationCardProps = {
  data: ReconciliationResponse
}

export function ReconciliationCard({data}: ReconciliationCardProps ) {

  return (
    <>
      <div className="flex flex-col py-4 lg:py-8 px-6 lg:px-12 space-y-2 mx-2 rounded-lg border border-black dark:border-white ">
        <div className="flex justify-between">
          <div className="bg-gray-400 dark:bg-gray-600 rounded-lg px-2 lg:px-4">John Doe</div>
          <div className="flex space-x-2">
            <Button className="bg-green-300 dark:bg-green-700 bShad">Accept</Button>
            <Button className="bShad" variant="destructive">Reject</Button>
          </div>
        </div>
        <div className="flex justify-between">
          <div className="lg:text-lg">{data.reconciled_medication}</div>
          <div>
            <div className={`bg-${assignColors(data.confidence_score)}-700 `}>{data.confidence_score}</div>
          </div>
        </div>
        <div className="flex lg:flex-row lg:justify-between bg-gray-400 dark:bg-gray-700 rounded-lg p-6 lg:p-12">
          <div>

          </div>
          <div className="flex flex-col">
            <div className="mx-auto">Recommended Actions</div>
            <ul>
              {data.recommended_actions.map((action) => (
                  <li>
                    action
                  </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </>
  )
}

type DataQualityCardProps = {
  data: DataQualityResponse
}

export function DataQualityCard({data}: DataQualityCardProps) {
  return (
    <>
      <div className="flex flex-col py-4 lg:py-8 px-6 lg:px-12 space-y-2 mx-2 rounded-lg border border-black dark:border-white ">
        <div className="flex justify-between">
          <div>{data.demographics.name}</div>
          <div className="flex space-x-2">
            <Button className="bg-green-300 dark:bg-green-700 bShad">Accept</Button>
            <Button className="bShad" variant="destructive">Reject</Button>
          </div>
        </div>
        <div className="flex lg:flex-row justify-around">
          <div className="flex flex-col">
            <div className="lg:text-lg">Breakdown</div>

            <div className="mr-1">Overall Score:</div>
            <div className={`bg-${assignColors(data.overall_score)}-700 `}>{data.overall_score}</div>

            <div>
              <div className={`bg-${assignColors(0)}-700 `}>{}</div>
            </div>
          </div>
          <div className="flex flex-col bg-gray-400 dark:bg-gray-700 rounded-lg p-6 lg:p-12">
            <div className="flex flex-col">
              <div className="mx-auto">Issues Detected</div>
                {data.issues_detected.map((issue) => (
                    <>
                    <div className="flex flex-row">
                      <div className={`bg-${SeverityMap.get(issue.severity)}-700`}></div>
                    </div>
                    </>
                ))}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

function assignColors(score: number): string {
    if (score > 75) {
      return "green"
    } else if (score > 50) {
      return "yellow"
    } 
    return "red"
}


export function Skeletons() {
  return (
    <div className="w-1/2 space-y-2 mx-4 lg:mx-8">
     {
      Array.from(Array(3), (_, i) => i).map((i) =>
        <SkeletonCard key={i}/>
      )
     }
    </div>
  )
}

function SkeletonCard({ ...props}) {
  return (
    <Card className="w-full max-h-32 " {...props}>
      <CardHeader>
        <div className="flex justify-between">
          <Skeleton className="h-4 w-1/4" />
          <Skeleton className="h-4 w-1/4" />
        </div>
        <Skeleton className="h-4 w-full" />
      </CardHeader>
      <CardContent>
        <Skeleton className="aspect-video w-full max-h-14 " />
      </CardContent>
    </Card>
  )
}