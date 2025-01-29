import { Skeleton } from "@/components/ui/skeleton"

export function ArticleCardSkeleton() {
  return (
    <div className="border-b border-zinc-200 dark:border-zinc-800 last:border-b p-6 px-0">
      {/* Header Section */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Skeleton className="h-6 w-6 rounded-full" />
          <Skeleton className="h-4 w-24" />
        </div>
        <Skeleton className="h-4 w-20" />
      </div>

      {/* Main Content */}
      <div className="flex flex-col gap-4">
        <div className="flex gap-6">
          <div className="flex-1">
            <Skeleton className="h-6 w-3/4 mb-2" />
            <Skeleton className="h-4 w-full mb-2" />
            <Skeleton className="h-4 w-2/3" />
          </div>
          <Skeleton className="w-[30%] aspect-square rounded-lg" />
        </div>

        {/* Footer Section */}
        <div className="flex items-center gap-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-4 rounded-full" />
          <Skeleton className="h-4 w-20" />
        </div>
      </div>
    </div>
  )
} 