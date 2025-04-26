export interface ArticleMetadata {
  source_url: string;
  author?: string | null;
  publish_date?: string | null;
  reading_time?: number | null;
}

export interface ArticleProgress {
  percentage: number;
  last_position: number;
  updated_at: string | null;
}

export interface ArticleTimestamps {
  saved_at: string | null;
  archived_at: string | null;
  deleted_at: string | null;
  created_at: string;
}

export interface Article {
  _id: string;
  title: string;
  short_description: string;
  metadata: ArticleMetadata;
  progress: ArticleProgress;
  timestamps: ArticleTimestamps;
  status: Array<'new' | 'saved' | 'deleted'>;
  type?: 'article' | 'bookmark';
}

export interface ArticleContent extends Article {
  content: string;
} 