'use client'

import { getUserArticle } from "@/services/articles"
import { notFound } from "next/navigation"
import { useEffect, useState } from "react"
import { MDXRemote } from 'next-mdx-remote'
import { serialize } from 'next-mdx-remote/serialize'
import { ArticleContent } from "@/components/article-content"
import { ArticleContent as ArticleType } from "@/types/article"

interface ClientArticleProps {
  articleId: string
}

export function ClientArticle({ articleId }: ClientArticleProps) {
  const [article, setArticle] = useState<ArticleType | null>(null)
  const [mdxSource, setMdxSource] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const userId = localStorage.getItem('user_id')
        if (!userId) {
          setError(true)
          return
        }

        const fetchedArticle = await getUserArticle(userId, articleId)
        
        if (fetchedArticle && fetchedArticle.content) {
          const mdxSource = await serialize(fetchedArticle.content)
          setMdxSource(mdxSource)
        }
        
        setArticle(fetchedArticle)
      } catch (err) {
        setError(true)
      } finally {
        setLoading(false)
      }
    }

    fetchArticle()
  }, [articleId])

  if (loading) {
    return null // Parent component handles loading state
  }

  if (error || !article || !article.content || !mdxSource) {
    notFound()
  }

  return (
    <ArticleContent article={article}>
      <MDXRemote {...mdxSource} />
    </ArticleContent>
  )
} 