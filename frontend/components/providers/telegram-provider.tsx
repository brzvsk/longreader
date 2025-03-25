'use client'

import { useEffect } from 'react'

export function TelegramProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const webApp = window.Telegram?.WebApp
    if (!webApp) {
      console.warn('Telegram WebApp not available')
      return
    }

    // Apply theme parameters as CSS variables
    const root = document.documentElement
    const { themeParams } = webApp
    
    root.style.setProperty('--tg-bg-color', themeParams.bg_color)
    root.style.setProperty('--tg-text-color', themeParams.text_color)
    root.style.setProperty('--tg-hint-color', themeParams.hint_color)
    root.style.setProperty('--tg-link-color', themeParams.link_color)
    root.style.setProperty('--tg-button-color', themeParams.button_color)
    root.style.setProperty('--tg-button-text-color', themeParams.button_text_color)

    // Set color scheme class
    root.classList.add(webApp.colorScheme === 'dark' ? 'dark' : 'light')

    // First tell Telegram the app is ready to be displayed
    webApp.ready()

    // Then expand the webapp to full height
    webApp.expand()

    // Initialize Telegram Analytics
    import('@telegram-apps/analytics').then((TelegramAnalytics) => {
      TelegramAnalytics.default.init({
        token: process.env.NEXT_PUBLIC_TELEGRAM_ANALYTICS_TOKEN || 'eyJhcHBfbmFtZSI6ImxvbmdyZWFkZXIiLCJhcHBfdXJsIjoiaHR0cHM6Ly90Lm1lL1JlYWRXYXRjaExhdGVyQm90IiwiYXBwX2RvbWFpbiI6Imh0dHBzOi8vbG9uZ3JlYWRlci5icnp2LnNrLyJ9!UX4UK+tLn6YLA0F6xYotLumBc7RuMKeXt3Qzr0DxeKI=',
        appName: 'longreader',
      });
    });
  }, [])

  return <>{children}</>
}