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

export function ArticleCardMenu({ articleId, sourceUrl, onDelete }: ArticleCardMenuProps) {
  const [open, setOpen] = React.useState(false)

  const handleCopyLink = async (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (sourceUrl) {
      await copyToClipboard(sourceUrl)
    }
    setOpen(false)
  }

  const handleOpenInBrowser = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (sourceUrl) {
      window.Telegram?.WebApp?.openLink(sourceUrl)
    }
    setOpen(false)
  }

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen)
  }

  return (
    <div onClick={handleClick}>
      <DropdownMenu open={open} onOpenChange={handleOpenChange}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreVertical className="h-4 w-4 text-muted-foreground" />
            <span className="sr-only">Open menu</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onSelect={() => setOpen(false)}>
            <Check className="mr-2 h-4 w-4" />
            Mark as Read
          </DropdownMenuItem>
          <DropdownMenuItem 
            onSelect={() => setOpen(false)}
            className="text-muted-foreground"
          >
            <Headphones className="mr-2 h-4 w-4" />
            Listen
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={() => setOpen(false)}>
            <Send className="mr-2 h-4 w-4" />
            Share...
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={handleCopyLink}>
            <Link2 className="mr-2 h-4 w-4" />
            Copy Link
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={handleOpenInBrowser}>
            <ExternalLink className="mr-2 h-4 w-4" />
            Open in Browser
          </DropdownMenuItem>
          <DropdownMenuItem onSelect={() => setOpen(false)}>
            <Archive className="mr-2 h-4 w-4" />
            Move to Archive
          </DropdownMenuItem>
          <DropdownMenuItem 
            onSelect={() => setOpen(false)} 
            className="text-red-600"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Remove
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
} 