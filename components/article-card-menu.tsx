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
import React from "react"

interface ArticleCardMenuProps {
  articleId: string
  sourceUrl?: string
  onDelete?: () => void
}

interface MenuAction {
  icon: LucideIcon
  label: string
  onClick: (e: React.MouseEvent) => void | Promise<void>
  className?: string
  disabled?: boolean
}

export function ArticleCardMenu({ articleId, sourceUrl, onDelete }: ArticleCardMenuProps) {
  const [open, setOpen] = React.useState(false)

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const createHandler = (action: (e: React.MouseEvent) => void | Promise<void>) => {
    return async (e: React.MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      await action(e)
      setOpen(false)
    }
  }

  const menuItems: MenuAction[] = [
    {
      icon: Check,
      label: "Mark as Read",
      onClick: () => {},
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
        if (sourceUrl) {
          window.Telegram?.WebApp?.openLink(sourceUrl)
        }
      },
    },
    {
      icon: Archive,
      label: "Move to Archive",
      onClick: () => {},
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
              onSelect={createHandler(item.onClick)}
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