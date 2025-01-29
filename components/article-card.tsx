import { Card, CardContent } from "@/components/ui/card"
import { Article } from "@/types/article"
import Image from "next/image"
import { Clock, Bookmark as BookmarkIcon } from "lucide-react"
import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface ArticleCardProps {
  article: Article
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <Link href={`/article/${article.id}`}>
      <div className="border-b border-zinc-200 dark:border-zinc-800 last:border-b p-6 px-0">
        {/* Header Section */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Avatar className="h-6 w-6">
              <AvatarImage src={article.sourceIconUrl} />
              <AvatarFallback>
                {(article.source || 'A').charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="text-xs text-muted-foreground">
              {article.author ? `@${article.author}` : article.source}
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <BookmarkIcon className="w-3.5 h-3.5 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">
              {(() => {
                const date = new Date(article.savedAt)
                const isCurrentYear = date.getFullYear() === new Date().getFullYear()
                return date.toLocaleDateString('en-US', {
                  month: 'long',
                  day: 'numeric',
                  year: isCurrentYear ? undefined : 'numeric'
                })
              })()}
            </span>
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
                {article.description}
              </p>
            </div>

            {article.thumbnailUrl && (
              <div className="relative shrink-0 w-[28%] self-top">
                <div className="aspect-square">
                  <Image
                    src={article.thumbnailUrl}
                    alt={article.title}
                    fill
                    className="object-cover rounded-sm"
                  />
                </div>
              </div>
            )}
          </div>
          
          {/* Footer Section */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1 text-xs">
              {article.readingTimeMinutes} min read
            </div>
            {article.readingProgress > 0 && (
              <>
                <span className="text-xs">•</span>
                <span className="text-xs">{article.readingProgress}% complete</span>
              </>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
} 