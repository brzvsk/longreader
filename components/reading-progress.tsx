'use client'

import { useEffect, useState, useCallback } from 'react'
import confetti from 'canvas-confetti'

interface ReadingProgressProps {
  initialProgress: number
  onProgressChange?: (progress: number) => void
  onNearEnd?: (isNearEnd: boolean) => void
}

export function ReadingProgress({ 
  initialProgress, 
  onProgressChange,
  onNearEnd 
}: ReadingProgressProps) {
  const [hasShownConfetti, setHasShownConfetti] = useState(false)
  const [progress, setProgress] = useState(initialProgress)

  // Initial scroll restoration
  useEffect(() => {
    if (initialProgress > 0) {
      setTimeout(() => {
        const documentHeight = document.documentElement.scrollHeight
        const windowHeight = window.innerHeight
        const scrollableHeight = documentHeight - windowHeight
        const scrollTo = (scrollableHeight * initialProgress) / 100
        
        window.scrollTo({
          top: scrollTo,
          behavior: 'smooth'
        })
      }, 100)
    }
  }, [initialProgress])

  const fireConfetti = useCallback(() => {
    const count = 200
    const defaults = {
      origin: { y: 0.7 }
    }

    function fire(particleRatio: number, opts: confetti.Options) {
      confetti({
        ...defaults,
        ...opts,
        particleCount: Math.floor(count * particleRatio)
      })
    }

    fire(0.25, { spread: 26, startVelocity: 55 })
    fire(0.2, { spread: 60 })
    fire(0.35, { spread: 100, decay: 0.91, scalar: 0.8 })
    fire(0.1, { spread: 120, startVelocity: 25, decay: 0.92, scalar: 1.2 })
    fire(0.1, { spread: 120, startVelocity: 45 })
  }, [])

  useEffect(() => {
    const handleScroll = () => {
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      const scrollTop = window.scrollY
      const scrollableHeight = documentHeight - windowHeight
      
      const newProgress = Math.min(Math.round((scrollTop / scrollableHeight) * 100), 100)
      setProgress(newProgress)
      onProgressChange?.(newProgress)

      // Notify when near end (95% or more)
      onNearEnd?.(newProgress >= 95)

      if (newProgress === 100 && !hasShownConfetti) {
        fireConfetti()
        setHasShownConfetti(true)
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [hasShownConfetti, fireConfetti, onProgressChange, onNearEnd])

  return null
} 