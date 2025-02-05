export interface ArticleMetadata {
  source_url: string;
  author?: string;
  publish_date?: string;
  reading_time: number;
}

export interface ArticleProgress {
  percentage: number;
  last_position: number;
  updated_at?: string;
}

export interface ArticleTimestamps {
  saved_at: string;
  archived_at?: string;
  deleted_at?: string;
  created_at: string;
}

export interface Article {
  _id: string;
  title: string;
  short_description: string;
  metadata: ArticleMetadata;
  progress: ArticleProgress;
  timestamps: ArticleTimestamps;
}

export interface ArticleContent extends Article {
  content: string | null;
} 