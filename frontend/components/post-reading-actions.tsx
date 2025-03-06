'use client'

import { Share, Archive, Check, Loader, Bookmark } from "lucide-react"
import { Button } from "./ui/button"
import { cn } from "@/lib/utils"
import { useEffect, useState, useCallback, useRef } from 'react'
import confetti from 'canvas-confetti'
import { updateArticleProgress, archiveArticle, shareArticle, unarchiveArticle, getUserArticle, saveArticle } from '@/services/articles'
import { useParams, useRouter } from 'next/navigation'
import { ArticleContent } from '@/types/article'

interface PostReadingActionsProps {
  isVisible: boolean
  initialProgress: number
  onProgressChange?: (progress: number) => void
  article?: ArticleContent
}

export function PostReadingActions({ 
  isVisible: initialIsVisible, 
  initialProgress,
  onProgressChange,
  article
}: PostReadingActionsProps) {
  const params = useParams()
  const router = useRouter()
  const articleId = params.id as string
  const [hasShownConfetti, setHasShownConfetti] = useState(false)
  const [progress, setProgress] = useState(initialProgress)
  const [isVisible, setIsVisible] = useState(initialIsVisible)
  const [isArchived, setIsArchived] = useState(false)
  const [isArchiving, setIsArchiving] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [shouldShowSave, setShouldShowSave] = useState(false)
  const updateTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const lastProgressRef = useRef(initialProgress)
  const actionButtonRef = useRef<HTMLButtonElement>(null)
  const lastScrollYRef = useRef(0)

  // Check if article was already at 100% progress
  useEffect(() => {
    if (initialProgress === 100) {
      setHasShownConfetti(true)
    }
  }, [initialProgress])

  // Determine if save button should be shown
  useEffect(() => {
    if (!article?.timestamps) return

    const isSaved = article.timestamps.saved_at !== null
    
    // Show save button if article is new (not saved)
    setShouldShowSave(!isSaved)
  }, [article])

  // Check initial article status
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const article = await getUserArticle(articleId)
        setIsArchived(!!article.timestamps.archived_at)
      } catch (error) {
        console.error('Failed to check article status:', error)
      }
    }
    checkStatus()
  }, [articleId])

  const showEmojis = useCallback((emoji: string) => {
    if (!actionButtonRef.current) return
    
    const buttonRect = actionButtonRef.current.getBoundingClientRect()
    const centerX = buttonRect.left + buttonRect.width / 2
    const centerY = buttonRect.top + buttonRect.height / 2
    
    // Create 5 emojis
    for (let i = 0; i < 5; i++) {
      const emojiElement = document.createElement('div')
      emojiElement.textContent = emoji
      emojiElement.style.position = 'fixed'
      emojiElement.style.zIndex = '100'
      emojiElement.style.fontSize = '24px'
      emojiElement.style.left = `${centerX}px`
      emojiElement.style.top = `${centerY}px`
      emojiElement.style.pointerEvents = 'none'
      emojiElement.style.transition = 'all 1s ease-out'
      document.body.appendChild(emojiElement)
      
      // Random direction for each emoji
      const angle = Math.random() * Math.PI * 2
      const distance = 50 + Math.random() * 100
      const finalX = centerX + Math.cos(angle) * distance
      const finalY = centerY + Math.sin(angle) * distance - 50 // Slight upward bias
      
      // Animate after a small delay to ensure the transition works
      setTimeout(() => {
        emojiElement.style.transform = `translate(${finalX - centerX}px, ${finalY - centerY}px) rotate(${Math.random() * 360}deg)`
        emojiElement.style.opacity = '0'
      }, 10)
      
      // Remove from DOM after animation completes
      setTimeout(() => {
        document.body.removeChild(emojiElement)
      }, 1100)
    }
  }, [])

  const showArchiveEmojis = useCallback(() => {
    showEmojis('📦')
  }, [showEmojis])

  const showUnarchiveEmojis = useCallback(() => {
    showEmojis('📚')
  }, [showEmojis])

  const handleSave = useCallback(async () => {
    if (isSaving) return
    
    // Trigger impact haptic feedback immediately on button tap
    const tg = window.Telegram?.WebApp
    if (tg?.hapticFeedback) {
      tg.hapticFeedback.impactOccurred('medium')
    }
    
    setIsSaving(true)
    try {
      await saveArticle(articleId)
      
      // Dispatch a custom event to notify that an article was saved
      window.dispatchEvent(new CustomEvent('article-saved'))
      
      // Navigate to home page
      router.push('/')
    } catch (error) {
      console.error('Failed to save article:', error)
      setIsSaving(false)
    }
  }, [articleId, isSaving, router])

  const handleArchive = useCallback(async () => {
    if (isArchiving) return
    
    // Trigger impact haptic feedback immediately on button tap
    const tg = window.Telegram?.WebApp
    if (tg?.hapticFeedback) {
      tg.hapticFeedback.impactOccurred('medium')
    }
    
    setIsArchiving(true)
    try {
      if (isArchived) {
        await unarchiveArticle(articleId)
        setIsArchived(false)
        showUnarchiveEmojis()
      } else {
        await archiveArticle(articleId)
        setIsArchived(true)
        showArchiveEmojis()
      }
      
    } catch (error) {
      console.error('Failed to update article archive status:', error)
      
    } finally {
      setIsArchiving(false)
    }
  }, [articleId, showArchiveEmojis, showUnarchiveEmojis, isArchiving, isArchived])

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

      // Determine scroll direction
      const isScrollingUp = scrollTop < lastScrollYRef.current
      lastScrollYRef.current = scrollTop

      // Show actions when:
      // 1. At the beginning (first screen)
      // 2. At the end (100% progress)
      // 3. When scrolling up
      if (boundedProgress >= 100 || boundedProgress <= 0 || isScrollingUp) {
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

  if (!article?.timestamps) {
    return null
  }

  return (
    <>
      {/* Progress bar */}
      <div className="fixed bottom-0 left-0 right-0 z-[60] bg-[var(--tg-bg-color)] backdrop-blur-sm">
        <div className="h-1 bg-[var(--tg-hint-color)]/30 mx-[env(safe-area-inset-left)] mb-[env(safe-area-inset-bottom)]">
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
            {shouldShowSave ? (
              <Button 
                variant="outline" 
                size="lg" 
                className={cn(
                  "flex items-center gap-2 border-[var(--tg-hint-color)] text-[var(--tg-text-color)] transition-all duration-300",
                  "hover:bg-[var(--tg-hint-color)]/10"
                )}
                onClick={handleSave}
                disabled={isSaving}
                ref={actionButtonRef}
              >
                <Bookmark className="w-4 h-4" />
                {isSaving ? 'Saving...' : 'Save to read later'}
              </Button>
            ) : (
              <Button 
                variant="outline" 
                size="lg" 
                className={cn(
                  "flex items-center gap-2 border-[var(--tg-hint-color)] text-[var(--tg-text-color)] transition-all duration-300",
                  isArchived ? "bg-[var(--tg-hint-color)]/10" : "hover:bg-[var(--tg-hint-color)]/10"
                )}
                onClick={handleArchive}
                disabled={isArchiving}
                ref={actionButtonRef}
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
            )}
          </div>
        </div>
      </div>
    </>
  )
} 