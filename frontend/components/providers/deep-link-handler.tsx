'use client'

import { useEffect, ReactNode, useState } from 'react'
import { DeepLinkProvider } from './deep-link-provider'
import { usePathname } from 'next/navigation'

interface DeepLinkHandlerProps {
  children: ReactNode
}

export function DeepLinkHandler({ children }: DeepLinkHandlerProps) {
  const pathname = usePathname()
  const [deepLinkState, setDeepLinkState] = useState({
    isDeepLink: false,
    articleId: null as string | null,
    handled: false
  })

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    const startParam = webApp?.initDataUnsafe?.start_param || ''
    const isDeepLink = startParam.startsWith('article_')
    const articleId = isDeepLink ? startParam.replace('article_', '') : null

    if (!deepLinkState.handled && isDeepLink) {
      setDeepLinkState({ isDeepLink: true, articleId, handled: true })
    } else if (pathname === '/') {
      setDeepLinkState({ isDeepLink: false, articleId: null, handled: true })
    }
  }, [pathname, deepLinkState.handled])

  return (
    <DeepLinkProvider isDeepLink={deepLinkState.isDeepLink} articleId={deepLinkState.articleId}>
      {children}
    </DeepLinkProvider>
  )
} 