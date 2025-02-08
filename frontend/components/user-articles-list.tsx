'use client'

import { useEffect, useState } from 'react'
import { ArticleCard } from "@/components/article-card"
import { ArticleCardSkeleton } from "@/components/article-card-skeleton"
import { getUserArticles, archiveArticle, unarchiveArticle, updateArticleProgress } from "@/services/articles"
import { Article } from '@/types/article'
import { cn } from '@/lib/utils'

type View = 'all' | 'archive'

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

  const inProgressArticles = articles
    .filter(article => article.progress.percentage > 0 && article.progress.percentage < 100 && !article.timestamps.archived_at)
    .sort((a, b) => {
      // Sort by last updated progress time if available
      if (a.progress.updated_at && b.progress.updated_at) {
        return new Date(b.progress.updated_at).getTime() - new Date(a.progress.updated_at).getTime()
      }
      // Fallback to progress percentage if no update time available
      return b.progress.percentage - a.progress.percentage
    })

  // Filter articles based on active view
  const viewArticles = articles.filter(article => {
    if (activeView === 'all') {
      return !article.timestamps.archived_at && article.progress.percentage === 0;
    } else {
      // Show both archived articles and completed (100% read) articles in Archive
      return article.timestamps.archived_at || article.progress.percentage === 100;
    }
  });

  if (loading) {
    return (
      <div className="flex flex-col gap-8">
        <div className="space-y-4">
          <div className="h-8 bg-muted animate-pulse rounded" style={{ width: '200px' }} />
          <div className="flex flex-col gap-4">
            {Array.from({length: 2}).map((_, i) => (
              <ArticleCardSkeleton key={`continue-${i}`} />
            ))}
          </div>
        </div>
        <div className="flex flex-col gap-4">
          {Array.from({length: 3}).map((_, i) => (
            <ArticleCardSkeleton key={`all-${i}`} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {inProgressArticles.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <span>🎯</span>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-600">Continue Reading</span>
          </h2>
          <div className="flex flex-col gap-4">
            {inProgressArticles.map((article) => (
              <ArticleCard 
                key={article._id} 
                article={article} 
                onArchive={() => handleArchive(article._id)}
                onUnarchive={() => handleUnarchive(article._id)}
                onProgressUpdate={(progress) => handleProgressUpdate(article._id, progress)}
              />
            ))}
          </div>
        </section>
      )}

      <section className="space-y-4">
        <div className="flex gap-6 items-center">
          <button
            onClick={() => setActiveView('all')}
            className="text-2xl font-bold flex items-center gap-2"
          >
            <span>💫</span>
            <span className={cn(
              activeView === 'all'
                ? "bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400"
                : "text-gray-400"
            )}>Unread</span>
          </button>
          <button
            onClick={() => setActiveView('archive')}
            className="text-2xl font-bold flex items-center gap-2"
          >
            <span>📦</span>
            <span className={cn(
              activeView === 'archive'
                ? "bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400"
                : "text-gray-400"
            )}>Archive</span>
          </button>
        </div>
        <div className="flex flex-col gap-4">
          {viewArticles.map((article) => (
            <ArticleCard 
              key={article._id} 
              article={article} 
              onArchive={() => handleArchive(article._id)}
              onUnarchive={() => handleUnarchive(article._id)}
              onProgressUpdate={(progress) => handleProgressUpdate(article._id, progress)}
            />
          ))}
        </div>
      </section>
    </div>
  )
} 