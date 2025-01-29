import { Article } from "@/types/article"

// This will be replaced with actual API call in the future
export async function getArticles(): Promise<Article[]> {
  // Simulate API call
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
  ]
} 