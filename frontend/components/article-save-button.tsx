import { Button } from "@/components/ui/button"
import { Bookmark, RotateCcw } from "lucide-react"
import { useState, useEffect } from "react"
import { saveArticle } from "@/services/articles"
import { ArticleContent } from "@/types/article"
import { useRouter } from "next/navigation"

interface ArticleSaveButtonProps {
  article: ArticleContent
}

export function ArticleSaveButton({ article }: ArticleSaveButtonProps) {
  const [isSaving, setIsSaving] = useState(false)
  const [shouldShow, setShouldShow] = useState(false)
  const router = useRouter()
  
  // Determine visibility based on article state
  useEffect(() => {
    const isDeleted = article.timestamps.deleted_at !== null
    const isSaved = article.timestamps.saved_at !== null
    
    // Show button if article is new (not saved) or deleted
    setShouldShow(!isSaved || isDeleted)
  }, [article])

  const handleSave = async () => {
    try {
      setIsSaving(true)
      await saveArticle(article._id)
      
      // Dispatch a custom event to notify that an article was saved
      window.dispatchEvent(new CustomEvent('article-saved'))
      
      // Instead of calling onSaved which reloads the page,
      // navigate directly to the home page
      router.push('/')
    } catch (error) {
      console.error('Failed to save article:', error)
      setIsSaving(false)
    }
  }

  if (!shouldShow) {
    return null
  }

  const isDeleted = article.timestamps.deleted_at !== null

  return (
    <div className="sticky top-0 z-50 p-4 bg-[var(--tg-bg-color)]">
      <Button
        size="lg"
        className="flex items-center gap-2"
        style={{
          backgroundColor: 'var(--tg-button-color)',
          color: 'var(--tg-button-text-color)'
        }}
        onClick={handleSave}
        disabled={isSaving}
      >
        {isDeleted ? (
          <>
            <RotateCcw className="w-4 h-4" />
            {isSaving ? 'Restoring...' : 'Restore article'}
          </>
        ) : (
          <>
            <Bookmark className="w-4 h-4" />
            {isSaving ? 'Saving...' : 'Save to read later'}
          </>
        )}
      </Button>
    </div>
  )
} 