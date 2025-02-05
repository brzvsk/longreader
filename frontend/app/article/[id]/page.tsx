import { Suspense } from "react"
import { ClientArticle } from "./client-article"
import { Skeleton } from "@/components/ui/skeleton"

interface PageProps {
  params: { id: string }
}

export default function ArticlePage({ params }: PageProps) {
  return (
    <Suspense fallback={<ArticleSkeleton />}>
      <ClientArticle articleId={params.id} />
    </Suspense>
  )
}

function ArticleSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-4 w-4/5" />
    </div>
  )
} 