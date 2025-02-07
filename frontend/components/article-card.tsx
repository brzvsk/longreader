import { Article } from "@/types/article"
import Image from "next/image"
import { 
  Bookmark as BookmarkIcon,
  Check as CheckIcon,
} from "lucide-react"
import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { ArticleCardMenu } from "./article-card-menu"
import { useState } from "react"
import { cn } from "@/lib/utils"

interface ArticleCardProps {
  article: Article
}

function getDomainFromUrl(url: string): string {
  try {
    const domain = new URL(url).hostname.replace('www.', '')
    return domain
  } catch {
    return url
  }
}

export function ArticleCard({ article }: ArticleCardProps) {
  const sourceName = getDomainFromUrl(article.metadata.source_url)
  const [progress, setProgress] = useState(article.progress.percentage)
  const isCompleted = progress === 100
  
  return (
    <Link href={`/article/${article._id}`}>
      <div className={cn(
        "border-b border-zinc-200 dark:border-zinc-800 last:border-b p-6 px-0 transition-all duration-200",
        isCompleted && "opacity-60 hover:opacity-100"
      )}>
        {/* Header Section */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Avatar className="h-6 w-6">
              <AvatarFallback>
                {sourceName.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="text-xs text-muted-foreground">
              {article.metadata.author ? `@${article.metadata.author}` : sourceName}
            </span>
          </div>

          <div className="flex items-center gap-1">
            <div className="flex items-center gap-1.5">
              <BookmarkIcon className="w-3.5 h-3.5 text-muted-foreground" />
              <span className="text-xs text-muted-foreground">
                {(() => {
                  const date = new Date(article.timestamps.saved_at)
                  const isCurrentYear = date.getFullYear() === new Date().getFullYear()
                  return date.toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: isCurrentYear ? undefined : 'numeric'
                  })
                })()}
              </span>
            </div>
            <ArticleCardMenu 
              articleId={article._id} 
              sourceUrl={article.metadata.source_url}
              onProgressUpdate={setProgress}
              progress={progress}
            />
          </div>
        </div>

        {/* Main Content */}
        <div className="flex flex-col gap-4">
          <div className="flex gap-6">
            <div className="flex-1">
              <h2 className="text-xl font-bold line-clamp-2 mb-2 font-sans">
                {article.title}
              </h2>
              <p className="text-base line-clamp-3">
                {article.short_description}
              </p>
            </div>
          </div>
          
          {/* Footer Section */}
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 text-xs">
                {article.metadata.reading_time} min read
              </div>
              {progress > 0 && (
                <>
                  <span className="text-xs">•</span>
                  {isCompleted ? (
                    <span className="text-xs flex items-center gap-1.5 text-green-600 font-medium">
                      completed
                      <div className="flex-shrink-0 rounded-full bg-green-600/10 p-0.5">
                        <CheckIcon className="w-3 h-3 text-green-600" />
                      </div>
                    </span>
                  ) : (
                    <span className="text-xs">{progress}% complete</span>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
} 