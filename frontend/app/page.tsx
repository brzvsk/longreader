import { UserArticlesList } from "@/components/user-articles-list"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <UserArticlesList />
      </main>
    </div>
  )
}
