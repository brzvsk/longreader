from typing import List
from fastapi import HTTPException
from bson import ObjectId
from ..models.article import Article, ArticleCollection
from ..database import articles

async def get_all_articles() -> ArticleCollection:
    cursor = articles.find()
    article_list = [Article(**doc) async for doc in cursor]
    return ArticleCollection(articles=article_list)


async def get_article_by_id(article_id: str) -> Article:
    try:
        article = await articles.find_one({"_id": ObjectId(article_id)})
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return Article(**article)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid article ID") 