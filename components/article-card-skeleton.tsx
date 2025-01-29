import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

export function ArticleCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        <div className="flex flex-row gap-4">
          <div className="flex-1 flex flex-col gap-2 p-4">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
            
            <div className="flex flex-wrap gap-4 mt-auto">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-20" />
            </div>
            
            <Skeleton className="h-4 w-24 mt-2" />
          </div>
          <Skeleton className="w-32 h-auto aspect-square" />
        </div>
      </CardContent>
    </Card>
  )
} 