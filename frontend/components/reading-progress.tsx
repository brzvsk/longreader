'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import confetti from 'canvas-confetti'
import { updateArticleProgress } from '@/services/articles'
import { useParams } from 'next/navigation'

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
  const params = useParams()
  const articleId = params.id as string
  const [hasShownConfetti, setHasShownConfetti] = useState(false)
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [progress, setProgress] = useState(initialProgress)
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastProgressRef = useRef(initialProgress)

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

  // Update progress on the server
  const updateProgress = useCallback((newProgress: number) => {
    lastProgressRef.current = newProgress
    updateArticleProgress(articleId, newProgress)
      .then(() => {
        console.log('Progress updated:', newProgress, 'for article:', articleId)
      })
      .catch(console.error)
  }, [articleId])

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

      // Debounce progress updates to avoid too many API calls
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }

      updateTimeoutRef.current = setTimeout(() => {
        updateProgress(newProgress)
      }, 1000)
    }

    console.log('Adding scroll event listener')
    window.addEventListener('scroll', handleScroll, { passive: true })
    
    return () => {
      console.log('Removing scroll event listener')
      window.removeEventListener('scroll', handleScroll)
      
      // Clear any pending timeout
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }
      
      // Send final progress update if it changed
      const finalProgress = lastProgressRef.current
      if (finalProgress !== initialProgress) {
        updateProgress(finalProgress)
      }
    }
  }, [hasShownConfetti, fireConfetti, onProgressChange, onNearEnd, initialProgress, updateProgress])

  return null
} 