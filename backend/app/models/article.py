from datetime import datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, List, Optional, Dict, Any
from enum import Enum
from bson import ObjectId


PyObjectId = Annotated[str, BeforeValidator(str)]

class ArticleStatus(str, Enum):
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"

class ArticleMetadata(BaseModel):
    source_url: str
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    reading_time: Optional[int] = None

class Article(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    status: ArticleStatus = ArticleStatus.PARSING
    title: str = Field(...)
    content: Optional[str] = None
    short_description: str = Field(...)
    metadata: ArticleMetadata = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

class UserArticleProgress(BaseModel):
    percentage: float = Field(default=0)
    last_position: int = Field(default=0)
    updated_at: Optional[datetime] = None

class UserArticleTimestamps(BaseModel):
    saved_at: datetime = Field(default_factory=datetime.utcnow)
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

class UserArticle(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId = Field(...)
    article_id: PyObjectId = Field(...)
    progress: UserArticleProgress = Field(default_factory=UserArticleProgress)
    timestamps: UserArticleTimestamps = Field(default_factory=UserArticleTimestamps)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

# Models for flattened user article response
class FlattenedTimestamps(BaseModel):
    saved_at: datetime
    archived_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime  # article creation time

class UserArticleFlat(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    title: str
    content: Optional[str] = None
    short_description: str
    metadata: ArticleMetadata
    progress: UserArticleProgress
    timestamps: FlattenedTimestamps

class UserArticleFlatCollection(BaseModel):
    articles: List[UserArticleFlat]