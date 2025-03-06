'use client'

import { useEffect, useState } from 'react'
import { ArticleCard } from "@/components/article-card"
import { ArticleCardSkeleton } from "@/components/article-card-skeleton"
import { getUserArticles, archiveArticle, unarchiveArticle, updateArticleProgress, deleteArticle } from "@/services/articles"
import { Article } from '@/types/article'
import { cn } from '@/lib/utils'

type View = 'all' | 'archive'

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24">
      <div className="relative mb-6">
        <svg width="0" height="0">
          <linearGradient id="blue-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop stopColor="#94b8e3" offset="0%" />
            <stop stopColor="#8ac4b0" offset="100%" />
          </linearGradient>
        </svg>
        {/* <Send className="w-16 h-16" style={{ stroke: 'url(#blue-gradient)', strokeWidth: 1.6 }} /> */}
      </div>
      <h2 className="text-2xl text-center font-bold mb-2" style={{ color: 'var(--tg-hint-color)' }}>
        Send link to the bot
      </h2>
      <p className="text-xl text-center" style={{ color: 'var(--tg-hint-color)' }}>
        It will appear here<br />for future readings 📚
      </p>
    </div>
  )
}

export function UserArticlesList() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)
  const [activeView, setActiveView] = useState<View>('all')

  const refreshArticles = async () => {
    try {
      const fetchedArticles = await getUserArticles()
      setArticles(fetchedArticles)
    } catch (error) {
      console.error('Failed to fetch articles:', error)
    }
  }

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const fetchedArticles = await getUserArticles()
        setArticles(fetchedArticles)
      } catch (error) {
        console.error('Failed to fetch articles:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchArticles()
  }, [])

  const handleArchive = async (articleId: string) => {
    try {
      await archiveArticle(articleId)
      await refreshArticles()
    } catch (error) {
      console.error('Failed to archive article:', error)
    }
  }

  const handleUnarchive = async (articleId: string) => {
    try {
      await unarchiveArticle(articleId)
      await refreshArticles()
    } catch (error) {
      console.error('Failed to unarchive article:', error)
    }
  }

  const handleProgressUpdate = async (articleId: string, progress: number) => {
    try {
      await updateArticleProgress(articleId, progress)
      await refreshArticles()
    } catch (error) {
      console.error('Failed to update article progress:', error)
    }
  }

  const handleDelete = async (articleId: string) => {
    try {
      await deleteArticle(articleId)
      await refreshArticles()
    } catch (error) {
      console.error('Failed to delete article:', error)
    }
  }

  // Filter articles based on active view
  const viewArticles = articles.filter(article => {
    if (activeView === 'all') {
      // Show all non-archived articles in the "Unread" section
      return !article.timestamps.archived_at;
    } else {
      // Show archived articles in Archive
      return article.timestamps.archived_at;
    }
  });

  if (loading) {
    return (
      <div className="flex flex-col gap-8">
        <div className="space-y-4">
          <div className="h-8 bg-muted animate-pulse rounded" style={{ width: '200px' }} />
          <div className="flex flex-col gap-4">
            {Array.from({length: 3}).map((_, i) => (
              <ArticleCardSkeleton key={`all-${i}`} />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      <section className="space-y-4">
        <div className="sticky top-0 bg-background py-4">
          <div className="flex gap-6 items-center">
            <button
              onClick={() => setActiveView('all')}
              className="text-2xl font-bold flex items-center gap-2"
            >
              <span>📚</span>
              <span className={cn(
                activeView === 'all'
                  ? "bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400"
                  : "text-gray-400"
              )}>Saved</span>
            </button>
            <button
              onClick={() => setActiveView('archive')}
              className="text-2xl font-bold flex items-center gap-2"
            >
              <span>📦</span>
              <span className={cn(
                activeView === 'archive'
                  ? "bg-clip-text text-transparent bg-gradient-to-r from-amber-400 to-orange-600"
                  : "text-gray-400"
              )}>Archive</span>
            </button>
          </div>
        </div>
        <div className="flex flex-col gap-4">
          {viewArticles.length > 0 ? (
            viewArticles.map((article) => (
              <ArticleCard 
                key={article._id} 
                article={article} 
                onArchive={() => handleArchive(article._id)}
                onUnarchive={() => handleUnarchive(article._id)}
                onProgressUpdate={(progress) => handleProgressUpdate(article._id, progress)}
                onDelete={() => handleDelete(article._id)}
              />
            ))
          ) : activeView === 'all' ? (
            <EmptyState />
          ) : null}
        </div>
      </section>
    </div>
  )
} 