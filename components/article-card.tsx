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
        <div className="flex flex-row gap-4">
          <div className="flex-1 flex flex-col gap-2 p-4">
            <h2 className="text-xl font-semibold line-clamp-2">{article.title}</h2>
            <p className="text-muted-foreground line-clamp-2">{article.description}</p>
            
            <div className="flex flex-wrap gap-4 mt-auto text-sm text-muted-foreground">
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
          {article.thumbnailUrl && (
            <div className="relative w-32 h-auto aspect-square">
              <Image
                src={article.thumbnailUrl}
                alt={article.title}
                fill
                className="object-cover"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
} 