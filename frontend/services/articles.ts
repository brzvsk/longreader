import { Article, ArticleContent } from "@/types/article"
import { api } from '@/lib/api'

function getUserId(): string {
  const userId = localStorage.getItem('user_id')
  if (!userId) {
    throw new Error('User not authenticated')
  }
  return userId
}

export async function getUserArticles(): Promise<Article[]> {
  const userId = getUserId()
  const response = await api.get<{ articles: Article[] }>(`/users/${userId}/articles`)
  return response.data.articles
}

export async function getUserArticle(articleId: string): Promise<ArticleContent> {
  const userId = getUserId()
  return (await api.get<ArticleContent>(`/users/${userId}/articles/${articleId}`)).data
}

export async function updateArticleProgress(articleId: string, progress: number): Promise<void> {
  const userId = getUserId()
  await api.put(`/users/${userId}/articles/${articleId}/progress?progress_percentage=${progress}`)
}

export async function archiveArticle(articleId: string): Promise<void> {
  const userId = getUserId()
  await api.put(`/users/${userId}/articles/${articleId}/archive`)
}

export async function unarchiveArticle(articleId: string): Promise<void> {
  const userId = getUserId()
  await api.put(`/users/${userId}/articles/${articleId}/unarchive`)
}

// export async function deleteArticle(userId: string, articleId: string): Promise<void> {
//   return apiRequest<void>(`/users/${userId}/articles/${articleId}`, {
//     method: 'DELETE',
//   })
// }
