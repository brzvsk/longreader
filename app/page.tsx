import { Article } from "@/types/article"
import { ArticleCard } from "@/components/article-card"
import { ArticleCardSkeleton } from "@/components/article-card-skeleton"
import { Suspense } from "react"

// Mock data - replace with your actual data fetching logic
async function getArticles(): Promise<Article[]> {
  // Simulate network delay
  await new Promise((resolve) => setTimeout(resolve, 700))
  
  return [
    {
      id: "1",
      title: "Understanding React Server Components",
      description: "A deep dive into React Server Components and how they change the way we build React applications.",
      source: "dev.to",
      author: "reactdev",
      readingTimeMinutes: 8,
      readingProgress: 45,
      savedAt: "2024-03-15T10:00:00Z",
      thumbnailUrl: "https://picsum.photos/seed/1/800/600",
    },
    {
      id: "2",
      title: "The Future of Web Development with Next.js 15",
      description: "Exploring the latest features and improvements in Next.js 15 and what they mean for developers.",
      source: "medium.com",
      readingTimeMinutes: 12,
      readingProgress: 0,
      savedAt: "2024-03-14T15:30:00Z",
      thumbnailUrl: "https://picsum.photos/seed/2/800/600",
    },
    // Add more mock articles as needed
  ]
}

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
            {[...Array(3)].map((_, i) => (
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
