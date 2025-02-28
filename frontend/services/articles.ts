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

export async function shareArticle(articleId: string): Promise<void> {
  console.log(`Initiating share for article: ${articleId}`)
  const userId = getUserId()
  
  const response = await api.post<{ message_id: string }>(`/users/${userId}/articles/${articleId}/share`)
  const messageId = response.data.message_id
  console.log(`Received message ID: ${messageId}`)
  
  if (window.Telegram?.WebApp?.shareMessage) {
    console.log('Calling Telegram WebApp shareMessage')
    return new Promise((resolve) => {
      window.Telegram.WebApp.shareMessage(messageId, (success) => {
        if (success) {
          console.log('Successfully shared message')
          resolve()
        } else {
          console.log('Share was cancelled or failed')
          resolve()
        }
      })
    })
  } else {
    console.error('Telegram share functionality not available')
    throw new Error('Telegram share functionality not available')
  }
}

export async function deleteArticle(articleId: string): Promise<void> {
  const userId = getUserId()
  await api.delete(`/users/${userId}/articles/${articleId}`)
}

export async function saveArticle(articleId: string): Promise<void> {
  const userId = getUserId()
  await api.post(`/users/${userId}/articles/${articleId}/save`)
}

export async function checkArticleStatus(articleId: string): Promise<{ status: 'new' | 'saved' | 'deleted' }> {
  const userId = getUserId()
  return (await api.get<{ status: 'new' | 'saved' | 'deleted' }>(`/users/${userId}/articles/${articleId}/status`)).data
}
