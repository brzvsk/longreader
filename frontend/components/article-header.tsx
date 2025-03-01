'use client'

import { ArticleMetadata } from "@/types/article"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ArticleOptionsMenu } from "./article-options-menu"
import { formatRelativeTime } from "@/utils/date-format"

interface ArticleHeaderProps {
  title: string
  progress: number
  metadata: ArticleMetadata
  articleId: string
  isArchived: boolean
  onDelete?: () => void
  onProgressUpdate?: (progress: number) => void
  onArchive?: () => void
  onUnarchive?: () => void
}

function getDomainFromUrl(url: string): string {
  try {
    const domain = new URL(url).hostname.replace('www.', '')
    return domain
  } catch {
    return url
  }
}

export function ArticleHeader({ 
  title, 
  progress, 
  metadata, 
  articleId,
  isArchived,
  onDelete,
  onProgressUpdate,
  onArchive,
  onUnarchive
}: ArticleHeaderProps) {
  // Format publish date if available
  const formattedDate = formatRelativeTime(metadata.publish_date || null)
  const sourceName = getDomainFromUrl(metadata.source_url)

  return (
    <>
      {/* Article Info Header */}
      <div className="container mx-auto px-4 pt-8 pb-8 relative">
        <div className="max-w-prose mx-auto">
          {/* Author */}
          <div className="flex items-center gap-2 mb-3">
            <Avatar className="h-6 w-6" style={{ backgroundColor: 'var(--tg-hint-color)', opacity: 0.2 }}>
              <AvatarFallback style={{ color: 'var(--tg-text-color)' }}>
                {sourceName.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="text-xs" style={{ color: 'var(--tg-hint-color)' }}>
              {metadata.author ? `@${metadata.author}` : sourceName}
            </span>
          </div>
          
          {/* Title */}
          <h1 className="text-2xl font-bold mb-3" style={{ color: 'var(--tg-text-color)' }}>{title}</h1>
          
          {/* Publish date and reading time */}
          <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--tg-hint-color)' }}>
            {formattedDate && (
              <>
                <span>{formattedDate}</span>
                <span>·</span>
              </>
            )}
            <span>{metadata.reading_time} min read</span>
            {progress > 0 && (
              <>
                <span>·</span>
                <span>{progress}% complete</span>
              </>
            )}
          </div>
        </div>
        
        <ArticleOptionsMenu 
          articleId={articleId}
          sourceUrl={metadata.source_url}
          progress={progress}
          isArchived={isArchived}
          onDelete={onDelete}
          onProgressUpdate={onProgressUpdate}
          onArchive={onArchive}
          onUnarchive={onUnarchive}
          variant="header"
        />
      </div>

      <div className="fixed bottom-0 left-0 right-0 z-50">
        <div className="h-1 bg-muted">
          <div 
            className="h-full bg-foreground transition-all duration-300" 
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </>
  )
} 