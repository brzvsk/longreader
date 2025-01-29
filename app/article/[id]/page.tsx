import { getArticleById } from "@/services/articles"
import { ArticleHeader } from "@/components/article-header"
import { notFound } from "next/navigation"
import { Suspense } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { MDXRemote } from 'next-mdx-remote/rsc'

export default async function ArticlePage({
  params: { id },
}: {
  params: { id: string }
}) {
  let article;
  try {
    article = await getArticleById(id)
  } catch {
    notFound()
  }

  return (
    <>
      <ArticleHeader title={article.title} initialProgress={article.readingProgress} />
      <main className="container mx-auto px-4 py-24">
        <article className="prose dark:prose-invert mx-auto">
          <Suspense fallback={<ArticleSkeleton />}>
            <MDXRemote source={article.content} />
          </Suspense>
        </article>
      </main>
    </>
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