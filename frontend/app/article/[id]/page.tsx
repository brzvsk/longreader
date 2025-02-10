import { Suspense } from "react"
import { ClientArticle } from "./client-article"
import { Skeleton } from "@/components/ui/skeleton"

export const runtime = 'edge'

interface PageProps {
  params: Promise<{ id: string }>
}

export default async function Page({ params }: PageProps) {
  const { id } = await params
  return (
    <Suspense fallback={<ArticleSkeleton />}>
      <ClientArticle articleId={id} />
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