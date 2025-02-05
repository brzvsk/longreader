'use client'

import { ArticleContent as ArticleType } from "@/types/article"
import { ArticleHeader } from "@/components/article-header"
import { ReadingProgress } from "@/components/reading-progress"
import { PostReadingActions } from "@/components/post-reading-actions"
import { useState } from "react"

interface ArticleContentProps {
  article: ArticleType
  children: React.ReactNode
}

export function ArticleContent({ article, children }: ArticleContentProps) {
  const [showActions, setShowActions] = useState(false)
  const [progress, setProgress] = useState(0)

  return (
    <>
      <ArticleHeader title={article.title} initialProgress={article.progress.percentage} />
      <main className="container mx-auto px-4 py-24">
        <article className="prose dark:prose-invert mx-auto">
          {children}
        </article>
      </main>
      <ReadingProgress 
        initialProgress={article.progress.percentage} 
        onProgressChange={setProgress}
        onNearEnd={setShowActions}
      />
      <PostReadingActions isVisible={showActions} />
    </>
  )
} 