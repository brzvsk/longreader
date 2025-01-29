import { getArticleById } from "@/services/articles"
import { notFound } from "next/navigation"
import { Suspense } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { MDXRemote } from 'next-mdx-remote/rsc'
import { ArticleContent } from "@/components/article-content"

interface PageProps {
  params: Promise<{ id: string }> | { id: string }
}

export default async function ArticlePage({ params }: PageProps) {
  const resolvedParams = await params
  
  let article;
  try {
    article = await getArticleById(resolvedParams.id)
  } catch {
    notFound()
  }

  return (
    <ArticleContent article={article}>
      <Suspense fallback={<ArticleSkeleton />}>
        <MDXRemote source={article.content} />
      </Suspense>
    </ArticleContent>
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