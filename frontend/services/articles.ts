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

export async function getArticles(): Promise<Article[]> {
  return apiRequest<Article[]>('/articles')
}

export async function getArticleById(id: string): Promise<ArticleContent> {
  return apiRequest<ArticleContent>(`/articles/${id}`)
}

// New functions for article management
// export async function saveArticle(url: string): Promise<Article> {
//   return apiRequest<Article>('/articles', {
//     method: 'POST',
//     body: JSON.stringify({ url }),
//   })
// }

// export async function updateReadingProgress(id: string, progress: number): Promise<void> {
//   return apiRequest<void>(`/articles/${id}/progress`, {
//     method: 'PUT',
//     body: JSON.stringify({ progress }),
//   })
// }

// export async function deleteArticle(id: string): Promise<void> {
//   return apiRequest<void>(`/articles/${id}`, {
//     method: 'DELETE',
//   })
// } 