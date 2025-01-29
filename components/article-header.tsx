'use client'

import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import { ReadingProgress } from "./reading-progress"

interface ArticleHeaderProps {
  title: string
  initialProgress: number
}

export function ArticleHeader({ title, initialProgress }: ArticleHeaderProps) {
  const [isVisible, setIsVisible] = useState(true)
  const [lastScrollY, setLastScrollY] = useState(0)
  const [progress, setProgress] = useState(initialProgress)

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight
      
      // Calculate reading progress
      const scrollProgress = (currentScrollY / (documentHeight - windowHeight)) * 100
      setProgress(Math.min(Math.round(scrollProgress), 100))
      
      // Handle header visibility
      setIsVisible(currentScrollY < lastScrollY || currentScrollY < 100)
      setLastScrollY(currentScrollY)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [lastScrollY])

  return (
    <>
      <header className={cn(
        "fixed top-0 left-0 right-0 bg-background/80 backdrop-blur-sm z-50 transition-transform duration-300",
        !isVisible && "-translate-y-16"
      )}>
        <div className="container mx-auto px-4">
          <div className="h-16 flex items-center gap-4">
            <Link href="/" className="hover:opacity-70">
              <ArrowLeft className="w-6 h-6" />
            </Link>
            <h1 className="font-medium truncate">{title}</h1>
          </div>
        </div>
      </header>
      <div className="fixed top-0 left-0 right-0 z-50">
        <div className="h-1 bg-muted">
          <div 
            className="h-full bg-foreground transition-all duration-300" 
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
      <ReadingProgress 
        initialProgress={initialProgress} 
        onProgressChange={setProgress}
      />
    </>
  )
} 