'use client'

import { ArticleContent as ArticleType } from "@/types/article"
import { ArticleHeader } from "@/components/article-header"
import { PostReadingActions } from "@/components/post-reading-actions"
import { deleteArticle, updateArticleProgress, archiveArticle, unarchiveArticle } from "@/services/articles"
import { useState } from "react"

interface ArticleContentProps {
  article: ArticleType
  children: React.ReactNode
}

export function ArticleContent({ article, children }: ArticleContentProps) {
  const [progress, setProgress] = useState(article.progress.percentage)
  const [isArchived, setIsArchived] = useState(!!article.timestamps.archived_at)
  
  const handleProgressUpdate = async (newProgress: number) => {
    try {
      await updateArticleProgress(article._id, newProgress)
      setProgress(newProgress)
    } catch (error) {
      console.error('Failed to update progress:', error)
    }
  }
  
  const handleArchive = async () => {
    try {
      await archiveArticle(article._id)
      setIsArchived(true)
    } catch (error) {
      console.error('Failed to archive article:', error)
    }
  }
  
  const handleUnarchive = async () => {
    try {
      await unarchiveArticle(article._id)
      setIsArchived(false)
    } catch (error) {
      console.error('Failed to unarchive article:', error)
    }
  }
  
  const handleDelete = async () => {
    try {
      await deleteArticle(article._id)
    } catch (error) {
      console.error('Failed to delete article:', error)
    }
  }

  return (
    <>
      <ArticleHeader 
        title={article.title} 
        progress={progress}
        metadata={article.metadata}
        articleId={article._id}
        isArchived={isArchived}
        onDelete={handleDelete}
        onProgressUpdate={handleProgressUpdate}
        onArchive={handleArchive}
        onUnarchive={handleUnarchive}
      />
      <main className="container mx-auto px-4 pb-16">
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