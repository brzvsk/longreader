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