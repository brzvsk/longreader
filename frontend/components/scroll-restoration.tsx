'use client'

import { useEffect } from 'react'

interface ScrollRestorationProps {
  progress: number
}

export function ScrollRestoration({ progress }: ScrollRestorationProps) {
  useEffect(() => {
    if (progress > 0) {
      // Wait for content to render
      setTimeout(() => {
        const documentHeight = document.documentElement.scrollHeight
        const windowHeight = window.innerHeight
        const scrollableHeight = documentHeight - windowHeight
        const scrollTo = (scrollableHeight * progress) / 100
        
        window.scrollTo({
          top: scrollTo,
          behavior: 'smooth'
        })
      }, 100)
    }
  }, [progress])

  return null
} 