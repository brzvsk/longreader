'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

export default function Template({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()

  // TODO: telegram script injects on every page change
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-web-app.js?56'
    script.async = false
    document.head.insertBefore(script, document.head.firstChild)

    script.onload = () => {
      const webApp = window.Telegram?.WebApp
      if (!webApp) return

      webApp.ready()
      
      if (pathname !== '/') {
        webApp.BackButton.show()
        webApp.BackButton.onClick(() => router.push('/')) // TODO: Add a back button to previous page, not just home
      } else {
        webApp.BackButton.hide()
      }
    }
  }, [pathname, router])

  return children
} 