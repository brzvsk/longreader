from datetime import datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, List, Optional


PyObjectId = Annotated[str, BeforeValidator(str)]

class ArticleMetadata(BaseModel):
    source_url: str
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    reading_time: int

class Article(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(...)
    content: str = Field(...)
    short_description: str = Field(...)
    metadata: ArticleMetadata = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class ArticleCollection(BaseModel):
    """
    A container holding a list of `Article` instances.
    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """
    articles: List[Article]

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

class UserArticleCollection(BaseModel):
    """
    A container holding a list of `UserArticle` instances.
    """
    articles: List[UserArticle]

class UserArticleDetail(BaseModel):
    article: Article
    user_article: UserArticle

class UserArticleDetailCollection(BaseModel):
    details: List[UserArticleDetail]

# New models for flattened user article response
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