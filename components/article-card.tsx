import { Card, CardContent } from "@/components/ui/card"
import { Article } from "@/types/article"
import Image from "next/image"
import { Calendar, Clock, Percent } from "lucide-react"

interface ArticleCardProps {
  article: Article
}

export function ArticleCard({ article }: ArticleCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <CardContent className="p-0">
        <div className="flex flex-col sm:flex-row gap-4">
          {article.thumbnailUrl && (
            <div className="relative w-full sm:w-48 h-48">
              <Image
                src={article.thumbnailUrl}
                alt={article.title}
                fill
                className="object-cover"
              />
            </div>
          )}
          <div className="flex flex-col gap-2 p-4">
            <h2 className="text-xl font-semibold line-clamp-2">{article.title}</h2>
            <p className="text-muted-foreground line-clamp-2">{article.description}</p>
            
            <div className="flex flex-wrap gap-4 mt-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {article.readingTimeMinutes} min read
              </div>
              <div className="flex items-center gap-1">
                <Percent className="w-4 h-4" />
                {article.readingProgress}% complete
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {new Date(article.savedAt).toLocaleDateString()}
              </div>
            </div>
            
            <div className="flex items-center gap-2 mt-2">
              <span className="text-sm text-muted-foreground">
                {article.author ? `@${article.author}` : article.source}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 