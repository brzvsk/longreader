import { createContext, useContext, ReactNode } from 'react'

interface DeepLinkContextType {
  isDeepLink: boolean
  articleId: string | null
}

const DeepLinkContext = createContext<DeepLinkContextType>({
  isDeepLink: false,
  articleId: null
})

export function useDeepLink() {
  return useContext(DeepLinkContext)
}

interface DeepLinkProviderProps {
  children: ReactNode
  isDeepLink: boolean
  articleId: string | null
}

export function DeepLinkProvider({ children, isDeepLink, articleId }: DeepLinkProviderProps) {
  return (
    <DeepLinkContext.Provider value={{ isDeepLink, articleId }}>
      {children}
    </DeepLinkContext.Provider>
  )
} 