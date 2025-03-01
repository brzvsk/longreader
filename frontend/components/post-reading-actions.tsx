'use client'

import { Share, Archive, Check, Loader } from "lucide-react"
import { Button } from "./ui/button"
import { cn } from "@/lib/utils"
import { useEffect, useState, useCallback, useRef } from 'react'
import confetti from 'canvas-confetti'
import { updateArticleProgress, archiveArticle, shareArticle } from '@/services/articles'
import { useParams } from 'next/navigation'

interface PostReadingActionsProps {
  isVisible: boolean
  initialProgress: number
  onProgressChange?: (progress: number) => void
}

export function PostReadingActions({ 
  isVisible: initialIsVisible, 
  initialProgress,
  onProgressChange 
}: PostReadingActionsProps) {
  const params = useParams()
  const articleId = params.id as string
  const [hasShownConfetti, setHasShownConfetti] = useState(false)
  const [progress, setProgress] = useState(initialProgress)
  const [isVisible, setIsVisible] = useState(initialIsVisible)
  const [isArchived, setIsArchived] = useState(false)
  const [isArchiving, setIsArchiving] = useState(false)
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastProgressRef = useRef(initialProgress)
  const archiveButtonRef = useRef<HTMLButtonElement>(null)

  const showArchiveEmojis = useCallback(() => {
    if (!archiveButtonRef.current) return
    
    const buttonRect = archiveButtonRef.current.getBoundingClientRect()
    const centerX = buttonRect.left + buttonRect.width / 2
    const centerY = buttonRect.top + buttonRect.height / 2
    
    // Create 5 archive emojis
    for (let i = 0; i < 5; i++) {
      const emoji = document.createElement('div')
      emoji.textContent = '📦'
      emoji.style.position = 'fixed'
      emoji.style.zIndex = '100'
      emoji.style.fontSize = '24px'
      emoji.style.left = `${centerX}px`
      emoji.style.top = `${centerY}px`
      emoji.style.pointerEvents = 'none'
      emoji.style.transition = 'all 1s ease-out'
      document.body.appendChild(emoji)
      
      // Random direction for each emoji
      const angle = Math.random() * Math.PI * 2
      const distance = 50 + Math.random() * 100
      const finalX = centerX + Math.cos(angle) * distance
      const finalY = centerY + Math.sin(angle) * distance - 50 // Slight upward bias
      
      // Animate after a small delay to ensure the transition works
      setTimeout(() => {
        emoji.style.transform = `translate(${finalX - centerX}px, ${finalY - centerY}px) rotate(${Math.random() * 360}deg)`
        emoji.style.opacity = '0'
      }, 10)
      
      // Remove from DOM after animation completes
      setTimeout(() => {
        document.body.removeChild(emoji)
      }, 1100)
    }
  }, [])

  // Helper function to safely trigger haptic feedback
  const triggerHapticFeedback = useCallback((type: 'success' | 'error') => {
    // Check if Telegram WebApp is available
    const tg = window.Telegram?.WebApp
    
    if (tg?.hapticFeedback) {
      if (type === 'success') {
        tg.hapticFeedback.notificationOccurred('success')
        tg.hapticFeedback.impactOccurred('medium')
      } else if (type === 'error') {
        tg.hapticFeedback.notificationOccurred('error')
      }
    }
  }, [])

  const handleArchive = useCallback(async () => {
    if (isArchiving || isArchived) return
    
    setIsArchiving(true)
    try {
      await archiveArticle(articleId)
      setIsArchived(true)
      showArchiveEmojis()
      
      // Trigger success haptic feedback
      triggerHapticFeedback('success')
    } catch (error) {
      console.error('Failed to archive article:', error)
      
      // Trigger error haptic feedback
      triggerHapticFeedback('error')
    } finally {
      setIsArchiving(false)
    }
  }, [articleId, showArchiveEmojis, isArchiving, isArchived, triggerHapticFeedback])

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

  // Handle scroll events to update progress
  useEffect(() => {
    const handleScroll = () => {
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }

      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      const scrollTop = window.scrollY
      const scrollableHeight = documentHeight - windowHeight

      const currentProgress = Math.round((scrollTop / scrollableHeight) * 100)
      const boundedProgress = Math.min(Math.max(currentProgress, 0), 100)

      setProgress(boundedProgress)
      onProgressChange?.(boundedProgress)

      // Show actions when near the end (90% or more)
      if (boundedProgress >= 100) {
        setIsVisible(true)
      } else {
        setIsVisible(false)
      }

      // Show confetti when reaching 100% for the first time
      if (boundedProgress === 100 && !hasShownConfetti) {
        fireConfetti()
        setHasShownConfetti(true)
      }

      // Debounce progress updates to the server
      updateTimeoutRef.current = setTimeout(() => {
        if (boundedProgress !== lastProgressRef.current) {
          updateProgress(boundedProgress)
        }
      }, 1000)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', handleScroll)
      if (updateTimeoutRef.current) {
        clearTimeout(updateTimeoutRef.current)
      }
    }
  }, [onProgressChange, updateProgress, hasShownConfetti, fireConfetti])

  const handleShare = async () => {
    try {
      await shareArticle(articleId)
    } catch (error) {
      console.error('Failed to share article:', error)
    }
  }

  return (
    <>
      {/* Progress bar */}
      <div className="fixed bottom-0 left-0 right-0 z-[60] bg-[var(--tg-bg-color)]">
        <div className="h-1 bg-[var(--tg-hint-color)]/30">
          <div 
            className="h-full transition-all duration-300 bg-gradient-to-r from-purple-400 to-pink-600"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Action buttons */}
      <div className={cn(
        "fixed bottom-1 left-0 right-0 bg-[var(--tg-bg-color)] border-t border-gray-200 transition-transform duration-500 ease-in-out transform z-40 shadow-sm",
        isVisible ? "translate-y-0" : "translate-y-full"
      )}>
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-center gap-4">
            <Button 
              size="lg" 
              className="flex items-center gap-2"
              style={{
                backgroundColor: 'var(--tg-button-color)',
                color: 'var(--tg-button-text-color)'
              }}
              onClick={handleShare}
            >
              <Share className="w-4 h-4" />
              Share
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className={cn(
                "flex items-center gap-2 border-[var(--tg-hint-color)] text-[var(--tg-text-color)] transition-all duration-300",
                isArchived ? "bg-[var(--tg-hint-color)]/10" : "hover:bg-[var(--tg-hint-color)]/10"
              )}
              onClick={handleArchive}
              disabled={isArchived || isArchiving}
              ref={archiveButtonRef}
            >
              {isArchived ? (
                <>
                  <Check className="w-4 h-4" />
                  Archived
                </>
              ) : isArchiving ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Archiving...
                </>
              ) : (
                <>
                  <Archive className="w-4 h-4" />
                  Archive
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </>
  )
} 