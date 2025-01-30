'use client'

import { useEffect } from 'react'

export default function Template({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-web-app.js?56'
    script.async = false
    document.head.insertBefore(script, document.head.firstChild)
  }, [])

  return children
} 