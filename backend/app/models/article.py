from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    source: str
    author: Optional[str] = None
    readingTimeMinutes: int
    readingProgress: int
    savedAt: str
    thumbnailUrl: Optional[str] = None
    sourceIconUrl: Optional[str] = None

class ArticleContent(BaseModel):
    id: str
    title: str
    content: str
    author: Optional[str] = None
    source: str
    readingTimeMinutes: int
    readingProgress: int
    savedAt: str
    thumbnailUrl: Optional[str] = None 