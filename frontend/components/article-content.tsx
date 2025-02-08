'use client'

import { ArticleContent as ArticleType } from "@/types/article"
// import { ArticleHeader } from "@/components/article-header"
import { PostReadingActions } from "@/components/post-reading-actions"

interface ArticleContentProps {
  article: ArticleType
  children: React.ReactNode
}

export function ArticleContent({ article, children }: ArticleContentProps) {
  return (
    <>
      {/* <ArticleHeader 
        title={article.title} 
        progress={progress}
      /> */}
      <main className="container mx-auto pt-16 px-4 py-24">
        <article className="prose dark:prose-invert mx-auto">
          {children}
        </article>
      </main>
      <PostReadingActions 
        isVisible={false}
        initialProgress={article.progress.percentage}
        onProgressChange={() => {}}
      />
    </>
  )
} 