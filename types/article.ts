export interface Article {
  id: string;
  title: string;
  description: string;
  source: string;
  author?: string;
  readingTimeMinutes: number;
  readingProgress: number;
  savedAt: string;
  thumbnailUrl?: string;
} 