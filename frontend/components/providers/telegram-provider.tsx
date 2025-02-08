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

    webApp.ready()
  }, [])

  return <>{children}</>
} 