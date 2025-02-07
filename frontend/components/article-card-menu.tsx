"use client"

import {
  Send,
  Link2,
  ExternalLink,
  Archive,
  Headphones,
  Trash2,
  Check,
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
  const isCompleted = progress === 100

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const createHandler = (action: () => void | Promise<void>) => {
    return async (e: React.MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      await action()
      setOpen(false)
    }
  }

  const menuItems: MenuAction[] = [
    {
      icon: Check,
      label: isCompleted ? "Mark as Unread" : "Mark as Read",
      onClick: async () => {
        const newProgress = isCompleted ? 0 : 100
        await updateArticleProgress(articleId, newProgress)
        onProgressUpdate?.(newProgress)
      },
    },
    {
      icon: Headphones,
      label: "Listen",
      onClick: () => {},
      className: "text-muted-foreground",
      disabled: true,
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
        } else {
          await archiveArticle(articleId)
          onArchive?.()
        }
      },
    },
    {
      icon: Trash2,
      label: "Remove",
      onClick: () => onDelete?.(),
      className: "text-red-600",
    },
  ]

  return (
    <div onClick={handleClick}>
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreVertical className="h-4 w-4 text-muted-foreground" />
            <span className="sr-only">Open menu</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {menuItems.map((item) => (
            <DropdownMenuItem
              key={item.label}
              onSelect={async () => {
                await item.onClick()
                setOpen(false)
              }}
              className={item.className}
              disabled={item.disabled}
            >
              <item.icon className="mr-2 h-4 w-4" />
              {item.label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
} 