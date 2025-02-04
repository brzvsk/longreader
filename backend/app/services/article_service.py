from typing import List
from fastapi import HTTPException
from ..models.article import Article, ArticleContent
from ..data.stub_data import articles, articles_content

async def get_all_articles() -> List[Article]:
    # Simulate database query
    return articles

async def get_article_by_id(article_id: str) -> ArticleContent:
    # Simulate database query
    if article_id not in articles_content:
        raise HTTPException(status_code=404, detail="Article not found")
    return articles_content[article_id] 