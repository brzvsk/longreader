import { Card, CardContent } from "@/components/ui/card"
import { Article } from "@/types/article"
import Image from "next/image"
import { Clock } from "lucide-react"
import Link from "next/link"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface ArticleCardProps {
  article: Article
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <Link href={`/article/${article.id}`}>
      <Card className="overflow-hidden hover:shadow-lg transition-shadow">
        <CardContent className="p-6">
          {/* Header Section */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Avatar className="h-6 w-6">
                <AvatarImage src={article.sourceIconUrl} />
                <AvatarFallback>
                  {(article.source || 'A').charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <span className="text-sm text-muted-foreground">
                {article.author ? `@${article.author}` : article.source}
              </span>
            </div>
            <span className="text-xs text-muted-foreground">
              {new Date(article.savedAt).toLocaleDateString()}
            </span>
          </div>

          {/* Main Content */}
          <div className="flex gap-6">
            <div className="flex-1">
              <h2 className="text-xl font-bold line-clamp-2 mb-2">
                {article.title}
              </h2>
              <p className="text-muted-foreground line-clamp-3 mb-4">
                {article.description}
              </p>
              
              {/* Footer Section */}
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {article.readingTimeMinutes} MIN READ
                </div>
                <span className="mx-2">•</span>
                <span>{article.readingProgress}% complete</span>
              </div>
            </div>

            {article.thumbnailUrl && (
              <div className="relative w-[30%] h-auto aspect-[4/3]">
                <Image
                  src={article.thumbnailUrl}
                  alt={article.title}
                  fill
                  className="object-cover rounded-lg"
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
} 