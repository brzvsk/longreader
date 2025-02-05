import { Article, ArticleContent } from "@/types/article"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL

const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
}

async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        ...DEFAULT_HEADERS,
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`)
    }
    
    // For DELETE requests or other requests that might not return data
    if (response.status === 204) {
      return {} as T
    }
    
    return await response.json()
  } catch (error) {
    console.error('API request error:', error)
    throw error
  }
}

export async function getUserArticles(userId: string): Promise<Article[]> {
  const response = await apiRequest<{ articles: Article[] }>(`/users/${userId}/articles`)
  return response.articles
}

export async function getUserArticle(userId: string, articleId: string): Promise<ArticleContent> {
  return apiRequest<ArticleContent>(`/users/${userId}/articles/${articleId}`)
}

// export async function updateArticleProgress(userId: string, articleId: string, progress: number): Promise<void> {
//   return apiRequest<void>(`/users/${userId}/articles/${articleId}/progress`, {
//     method: 'PUT',
//     body: JSON.stringify({ progress_percentage: progress }),
//   })
// }

// export async function archiveArticle(userId: string, articleId: string): Promise<void> {
//   return apiRequest<void>(`/users/${userId}/articles/${articleId}/archive`, {
//     method: 'PUT',
//   })
// }

// export async function deleteArticle(userId: string, articleId: string): Promise<void> {
//   return apiRequest<void>(`/users/${userId}/articles/${articleId}`, {
//     method: 'DELETE',
//   })
// }
