"use client"

import {
  Send,
  Link2,
  ExternalLink,
  Archive,
  Headphones,
  Trash2,
//  Check,
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
import { updateArticleProgress, archiveArticle, unarchiveArticle, shareArticle } from "@/services/articles"
import React from "react"

interface ArticleCardMenuProps {
  articleId: string
  sourceUrl?: string
  onDelete?: () => void
  onProgressUpdate?: (progress: number) => void
  onArchive?: () => void
  onUnarchive?: () => void
  progress?: number
  isArchived?: boolean
}

interface MenuAction {
  icon: LucideIcon
  label: string
  onClick: () => void | Promise<void>
  className?: string
  disabled?: boolean
  style?: React.CSSProperties
}

export function ArticleCardMenu({ 
  articleId, 
  sourceUrl, 
  onDelete,
  onProgressUpdate,
  onArchive,
  onUnarchive,
  progress = 0,
  isArchived = false
}: ArticleCardMenuProps) {
  const [open, setOpen] = React.useState(false)
//  const isCompleted = progress === 100

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
      onClick: async () => {
        try {
          await shareArticle(articleId)
        } catch (error) {
          console.error('Failed to share article:', error)
        }
      },
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
              }
            }
          )
        } else {
          onDelete?.()
        }
      },
      style: { color: 'var(--tg-destructive)' }
    },
  ]

  return (
    <div onClick={handleClick}>
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreVertical className="h-4 w-4" style={{ color: 'var(--tg-hint-color)' }} />
            <span className="sr-only">Open menu</span>
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
