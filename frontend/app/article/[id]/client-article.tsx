'use client'

import { getUserArticle } from "@/services/articles"
import { notFound } from "next/navigation"
import { useEffect, useState } from "react"
import { MDXRemote } from 'next-mdx-remote'
import { serialize } from 'next-mdx-remote/serialize'
import { ArticleContent } from "@/components/article-content"
import { ArticleContent as ArticleType } from "@/types/article"
import { MDXRemoteSerializeResult } from 'next-mdx-remote'
import { PostReadingActions } from '@/components/post-reading-actions'
import { useDeepLink } from '@/components/providers/deep-link-provider'

interface ClientArticleProps {
  articleId: string
}

// Custom link component that opens links in a new tab
const CustomLink = ({ href, children }: { href: string; children: React.ReactNode }) => (
  <a href={href} target="_blank" rel="noopener noreferrer">
    {children}
  </a>
)

export function ClientArticle({ articleId }: ClientArticleProps) {
  const [article, setArticle] = useState<ArticleType | null>(null)
  const [mdxSource, setMdxSource] = useState<MDXRemoteSerializeResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  useDeepLink()

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        const fetchedArticle = await getUserArticle(articleId)
        
        if (fetchedArticle && fetchedArticle.content) {
          const mdxSource = await serialize(fetchedArticle.content)
          setMdxSource(mdxSource)
        }
        
        setArticle(fetchedArticle)
      } catch {
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
    <div className="relative">
      <ArticleContent article={article}>
        <MDXRemote {...mdxSource} components={{ a: CustomLink }} />
      </ArticleContent>
      <PostReadingActions
        isVisible={!!article.timestamps.saved_at}
        initialProgress={article.progress.percentage}
        article={article}
      />
    </div>
  )
} 