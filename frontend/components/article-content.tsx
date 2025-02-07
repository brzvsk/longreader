'use client'

import { ArticleContent as ArticleType } from "@/types/article"
// import { ArticleHeader } from "@/components/article-header"
import { PostReadingActions } from "@/components/post-reading-actions"
import { useState } from "react"

interface ArticleContentProps {
  article: ArticleType
  children: React.ReactNode
}

export function ArticleContent({ article, children }: ArticleContentProps) {
  const [progress, setProgress] = useState(article.progress.percentage)

  return (
    <>
      {/* <ArticleHeader 
        title={article.title} 
        progress={progress}
      /> */}
      <main className="container mx-auto px-4 py-24">
        <article className="prose dark:prose-invert mx-auto">
          {children}
        </article>
      </main>
      <PostReadingActions 
        isVisible={false}
        initialProgress={article.progress.percentage}
        onProgressChange={setProgress}
      />
    </>
  )
} 