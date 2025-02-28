'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { UserArticlesList } from '@/components/user-articles-list'
import { useDeepLink } from '@/components/providers/deep-link-provider'

export default function Home() {
  const router = useRouter()
  const { isDeepLink, articleId } = useDeepLink()

  useEffect(() => {
    if (isDeepLink && articleId) {
      router.push(`/article/${articleId}`)
    }
  }, [isDeepLink, articleId, router])

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <UserArticlesList />
      </main>
    </div>
  )
}
