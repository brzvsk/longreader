'use client'

import { useEffect } from 'react'

export function TelegramProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (!webApp) {
      console.warn('Telegram WebApp not available')
      return
    }

    webApp.ready()
  }, [])

  return <>{children}</>
} 