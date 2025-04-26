import { Article } from "@/types/article"
import { 
  Bookmark as BookmarkIcon,
  Check as CheckIcon,
} from "lucide-react"
import Link from "next/link"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { ArticleOptionsMenu } from "./article-options-menu"
import { useState } from "react"
import { cn } from "@/lib/utils"
import { formatRelativeTime } from "@/utils/date-format"

interface ArticleCardProps {
  article: Article
  onArchive?: () => void
  onUnarchive?: () => void
  onProgressUpdate?: (progress: number) => void
  onDelete?: () => void
}

function getDomainFromUrl(url: string): string {
  try {
    const domain = new URL(url).hostname.replace('www.', '')
    return domain
  } catch {
    return url
  }
}

function getHumanReadablePath(url: string): string {
  try {
    const { pathname } = new URL(url);
    // Remove leading/trailing slashes and split by '/'
    const segments = pathname.replace(/^\/+|\/+$/g, '').split('/');
    // Split by '-' and remove file extensions, capitalize words
    const words = segments.flatMap(segment =>
      segment
        .replace(/\.[^/.]+$/, '') // remove file extension
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    );
    return words.join(' ');
  } catch {
    return url;
  }
}

export function ArticleCard({ article, onArchive, onUnarchive, onProgressUpdate, onDelete }: ArticleCardProps) {
  const sourceName = getDomainFromUrl(article.metadata.source_url)
  const [progress, setProgress] = useState(article.progress.percentage)
  const isCompleted = progress === 100
  const isArchived = !!article.timestamps.archived_at
  
  const handleProgressUpdate = (newProgress: number) => {
    setProgress(newProgress)
    onProgressUpdate?.(newProgress)
  }

  return (
    <div className={cn(
      "border-b border-zinc-200 dark:border-zinc-800 last:border-b p-6 px-0 transition-all duration-200",
      isCompleted && "opacity-60 hover:opacity-100"
    )}>
      {/* Header Section */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Avatar className="h-6 w-6" style={{ backgroundColor: 'var(--tg-hint-color)', opacity: 0.2 }}>
            <AvatarFallback style={{ color: 'var(--tg-text-color)' }}>
              {sourceName.charAt(0).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <span className="text-xs" style={{ color: 'var(--tg-hint-color)' }}>
            {article.metadata.author ? `@${article.metadata.author}` : sourceName}
          </span>
        </div>

        <div className="flex items-center gap-1">
          <div className="flex items-center gap-1.5">
            <BookmarkIcon className="w-3.5 h-3.5" style={{ color: 'var(--tg-hint-color)' }} />
            <span className="text-xs" style={{ color: 'var(--tg-hint-color)' }}>
              {formatRelativeTime(article.timestamps.saved_at)}
            </span>
          </div>
          <ArticleOptionsMenu 
            articleId={article._id} 
            sourceUrl={article.metadata.source_url}
            onProgressUpdate={handleProgressUpdate}
            onArchive={onArchive}
            onUnarchive={onUnarchive}
            onDelete={onDelete}
            progress={progress}
            isArchived={isArchived}
            variant="card"
          />
        </div>
      </div>

      {/* Main Content */}
      <Link 
        href={`/article/${article._id}`} 
        className="block"
      >
        <div className="flex flex-col gap-4">
          <div className="flex gap-6">
            <div className="flex-1">
              <h2 className="text-xl font-bold line-clamp-2 mb-2 font-sans" style={{ color: 'var(--tg-text-color)' }}>
                {article.title || getHumanReadablePath(article.metadata.source_url)}
              </h2>
              <p className="text-base line-clamp-3" style={{ color: 'var(--tg-text-color)' }}>
                {article.short_description}
              </p>
            </div>
          </div>
          
          {/* Footer Section */}
          {(article.metadata.reading_time || progress > 0) && (
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                {/* Only show reading time if it exists */}
                {article.metadata.reading_time ? (
                  <div className="flex items-center gap-1 text-xs" style={{ color: 'var(--tg-hint-color)' }}>
                    {article.metadata.reading_time} min read
                  </div>
                ) : null}
                {progress > 0 && (
                  <>
                    <span className="text-xs" style={{ color: 'var(--tg-hint-color)' }}>•</span>
                    {isCompleted ? (
                      <span className="text-xs flex items-center gap-1.5 text-green-600 font-medium">
                        completed
                        <div className="flex-shrink-0 rounded-full bg-green-600/10 p-0.5">
                          <CheckIcon className="w-3 h-3 text-green-600" />
                        </div>
                      </span>
                    ) : (
                      <span className="text-xs" style={{ color: 'var(--tg-hint-color)' }}>{progress}% complete</span>
                    )}
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </Link>
    </div>
  )
} 