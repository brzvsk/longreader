'use client'

import { Share, Archive } from "lucide-react"
import { Button } from "./ui/button"
import { cn } from "@/lib/utils"

interface PostReadingActionsProps {
  isVisible: boolean
}

export function PostReadingActions({ isVisible }: PostReadingActionsProps) {
  return (
    <div className={cn(
      "fixed bottom-0 left-0 right-0 bg-background/80 backdrop-blur-sm border-t transition-transform duration-500 ease-in-out transform z-40",
      isVisible ? "translate-y-0" : "translate-y-full"
    )}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-center gap-4">
          <Button variant="outline" size="lg" className="flex items-center gap-2">
            <Share className="w-4 h-4" />
            Share
          </Button>
          <Button size="lg" className="flex items-center gap-2">
            <Archive className="w-4 h-4" />
            Archive
          </Button>
        </div>
      </div>
    </div>
  )
} 