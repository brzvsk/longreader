"use client"

import {
  Send,
  Link2,
  ExternalLink,
  Archive,
  Headphones,
  Trash2,
  MoreVertical,
  LucideIcon,
} from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { copyToClipboard } from "@/utils/clipboard"
import { updateArticleProgress, archiveArticle, unarchiveArticle } from "@/services/articles"
import { useRouter } from "next/navigation"
import React from "react"

interface ArticleOptionsMenuProps {
  articleId: string
  sourceUrl: string
  onDelete?: () => void
  onProgressUpdate?: (progress: number) => void
  onArchive?: () => void
  onUnarchive?: () => void
  progress: number
  isArchived: boolean
  variant?: "card" | "header"
  className?: string
}

interface MenuAction {
  icon: LucideIcon
  label: string
  onClick: () => void | Promise<void>
  className?: string
  disabled?: boolean
  style?: React.CSSProperties
}

export function ArticleOptionsMenu({ 
  articleId, 
  sourceUrl, 
  onDelete,
  onProgressUpdate,
  onArchive,
  onUnarchive,
  progress,
  isArchived,
  variant = "header",
  className
}: ArticleOptionsMenuProps) {
  const [open, setOpen] = React.useState(false)
  const router = useRouter()

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const menuItems: MenuAction[] = [
    {
      icon: Headphones,
      label: "Listen",
      onClick: () => {},
      disabled: true,
      style: { color: 'var(--tg-hint-color)' }
    },
    {
      icon: Send,
      label: "Share...",
      onClick: () => {},
    },
    {
      icon: Link2,
      label: "Copy Link",
      onClick: async () => {
        if (sourceUrl) {
          await copyToClipboard(sourceUrl)
        }
      },
    },
    {
      icon: ExternalLink,
      label: "Open in Browser",
      onClick: () => {
        if (sourceUrl && window.Telegram?.WebApp) {
          window.open(sourceUrl, '_blank')
        }
      },
    },
    {
      icon: Archive,
      label: isArchived ? "Unarchive" : "Archive",
      onClick: async () => {
        if (isArchived) {
          await unarchiveArticle(articleId)
          onUnarchive?.()
          if (progress === 100) {
            await updateArticleProgress(articleId, 0)
            onProgressUpdate?.(0)
          }
        } else {
          await archiveArticle(articleId)
          onArchive?.()
          // Only navigate away if we're on the article page (header variant)
          if (variant === "header") {
            router.push('/')
          }
        }
      },
    },
    {
      icon: Trash2,
      label: "Remove",
      onClick: () => {
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showConfirm(
            "Are you sure you want to remove this article?",
            (isConfirmed) => {
              if (isConfirmed) {
                onDelete?.()
                // Only navigate away if we're on the article page (header variant)
                if (variant === "header") {
                  router.push('/')
                }
              }
            }
          )
        } else {
          onDelete?.()
          // Only navigate away if we're on the article page (header variant)
          if (variant === "header") {
            router.push('/')
          }
        }
      },
      style: { color: 'var(--tg-destructive)' }
    },
  ]

  const IconComponent = MoreVertical
  const buttonClassName = variant === "card" ? "h-8 w-8" : "h-8 w-8 absolute right-4 top-8"
  const iconSize = variant === "card" ? "h-4 w-4" : "h-5 w-5"

  return (
    <div onClick={handleClick} className={className}>
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className={buttonClassName}>
            <IconComponent className={iconSize} style={{ color: 'var(--tg-hint-color)' }} />
            <span className="sr-only">Options</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent 
          align="end" 
          className="bg-transparent border-none shadow-lg"
          style={{ 
            backgroundColor: 'var(--tg-bg-color)',
            color: 'var(--tg-text-color)',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.2)'
          }}
        >
          {menuItems.map((item) => (
            <DropdownMenuItem
              key={item.label}
              onSelect={async () => {
                await item.onClick()
                setOpen(false)
              }}
              disabled={item.disabled}
              className="hover:bg-opacity-10 focus:bg-opacity-10 focus:bg-[var(--tg-hint-color)] hover:bg-[var(--tg-hint-color)]"
              style={{
                color: item.disabled ? 'var(--tg-hint-color)' : 
                      item.label === 'Remove' ? 'var(--tg-destructive)' : 
                      'var(--tg-text-color)'
              }}
            >
              <item.icon 
                className="mr-2 h-4 w-4" 
                style={{
                  color: item.disabled ? 'var(--tg-hint-color)' : 
                        item.label === 'Remove' ? 'var(--tg-destructive)' : 
                        'var(--tg-text-color)'
                }} 
              />
              {item.label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
} 
