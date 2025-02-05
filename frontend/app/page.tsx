import { UserArticlesList } from "@/components/user-articles-list"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Longreader</h1>
        <UserArticlesList />
      </main>
    </div>
  )
}
