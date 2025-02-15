import { Button } from "@/components/ui/button"
import { Bookmark, RotateCcw } from "lucide-react"
import { useState } from "react"
import { saveArticle } from "@/services/articles"
import { ArticleContent } from "@/types/article"

interface ArticleSaveButtonProps {
  article: ArticleContent
  onSaved?: () => void
}

export function ArticleSaveButton({ article, onSaved }: ArticleSaveButtonProps) {
  const [isSaving, setIsSaving] = useState(false)

  const handleSave = async () => {
    try {
      setIsSaving(true)
      await saveArticle(article._id)
      onSaved?.()
    } catch (error) {
      console.error('Failed to save article:', error)
    } finally {
      setIsSaving(false)
    }
  }

  // Only show the button for new or deleted articles
  console.log('Article status:', article.status, 'Timestamps:', article.timestamps)
  const isDeleted = article.timestamps.deleted_at !== null
  const isSaved = article.timestamps.saved_at !== null

  // Show button if article is new (not saved) or deleted
  if (isSaved && !isDeleted) {
    return null
  }

  return (
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
  )
} 