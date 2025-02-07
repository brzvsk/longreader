'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export default function Template({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (!webApp) return

    // TODO: add a back button to previous page, not just home
    if (pathname !== '/') {
      webApp.BackButton.show()
      webApp.BackButton.onClick(() => router.push('/'))
    } else {
      webApp.BackButton.hide()
    }
  }, [pathname, router])

  return children
} 