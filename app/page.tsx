import { ArticleCard } from "@/components/article-card"
import { ArticleCardSkeleton } from "@/components/article-card-skeleton"
import { Suspense } from "react"
import { getArticles } from "@/services/articles"

async function ArticlesList() {
  const articles = await getArticles()
  
  return (
    <div className="flex flex-col gap-4">
      {articles.map((article) => (
        <ArticleCard key={article.id} article={article} />
      ))}
    </div>
  )
}

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Reading List</h1>
        <Suspense fallback={
          <div className="flex flex-col gap-4">
            {Array.from({length: 3}).map((_, i) => (
              <ArticleCardSkeleton key={i} />
            ))}
          </div>
        }>
          <ArticlesList />
        </Suspense>
      </main>
    </div>
  )
}
