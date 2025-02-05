'use client'

import { useEffect, useState } from 'react'
import { ArticleCard } from "@/components/article-card"
import { ArticleCardSkeleton } from "@/components/article-card-skeleton"
import { getUserArticles } from "@/services/articles"
import { Article } from '@/types/article'

export function UserArticlesList() {
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

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

  if (loading) {
    return (
      <div className="flex flex-col gap-4">
        {Array.from({length: 3}).map((_, i) => (
          <ArticleCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      {articles.map((article) => (
        <ArticleCard key={article._id} article={article} />
      ))}
    </div>
  )
} 