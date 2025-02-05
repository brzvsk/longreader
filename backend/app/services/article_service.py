from typing import List
from fastapi import HTTPException
from bson import ObjectId
from ..models.article import Article, ArticleCollection, FlattenedTimestamps, UserArticle, UserArticleCollection, UserArticleDetail, UserArticleDetailCollection, UserArticleFlat, UserArticleFlatCollection
from ..database import articles, user_articles
from datetime import datetime

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

async def get_user_articles(user_id: str) -> ArticleCollection:
    """Get all articles saved by a specific user"""
    # Get user's article references
    cursor = user_articles.find({"user_id": user_id, "timestamps.deleted_at": None})
    user_article_list = [UserArticle(**doc) async for doc in cursor]
    
    if not user_article_list:
        return ArticleCollection(articles=[])
    
    # Get the actual articles
    article_ids = [ObjectId(ua.article_id) for ua in user_article_list]
    articles_cursor = articles.find({"_id": {"$in": article_ids}})
    article_list = [Article(**doc) async for doc in articles_cursor]
    
    return ArticleCollection(articles=article_list)

async def save_article_for_user(user_id: str, article_id: str) -> UserArticle:
    """Save an article for a specific user"""
    try:
        # Check if article exists
        article = await get_article_by_id(article_id)
        
        # Create user article reference
        user_article = UserArticle(
            user_id=user_id,
            article_id=ObjectId(article_id)
        )
        
        # Insert into database
        result = await user_articles.insert_one(user_article.model_dump(by_alias=True))
        
        # Return created user article
        created = await user_articles.find_one({"_id": result.inserted_id})
        return UserArticle(**created)
    except Exception as e:
        if "duplicate key error" in str(e).lower():
            raise HTTPException(status_code=400, detail="Article already saved for this user")
        raise HTTPException(status_code=500, detail="Failed to save article")

async def update_article_progress(user_id: str, article_id: str, progress_percentage: float) -> UserArticle:
    """Update reading progress for a user's article"""
    try:
        # Update progress
        result = await user_articles.find_one_and_update(
            {
                "user_id": user_id,
                "article_id": ObjectId(article_id),
                "timestamps.deleted_at": None
            },
            {
                "$set": {
                    "progress.percentage": progress_percentage,
                    "progress.updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="User article not found")
            
        return UserArticle(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update progress")

async def archive_user_article(user_id: str, article_id: str) -> UserArticle:
    """Archive an article for a user"""
    try:
        result = await user_articles.find_one_and_update(
            {
                "user_id": user_id,
                "article_id": ObjectId(article_id),
                "timestamps.deleted_at": None
            },
            {
                "$set": {
                    "timestamps.archived_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="User article not found")
            
        return UserArticle(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to archive article")

async def delete_user_article(user_id: str, article_id: str) -> UserArticle:
    """Soft delete an article for a user"""
    try:
        result = await user_articles.find_one_and_update(
            {
                "user_id": user_id,
                "article_id": ObjectId(article_id),
                "timestamps.deleted_at": None
            },
            {
                "$set": {
                    "timestamps.deleted_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="User article not found")
            
        return UserArticle(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete article")

async def get_user_articles_details(user_id: str) -> UserArticleDetailCollection:
    """Get all articles with user article data for a specific user"""
    # Get user's article references
    cursor = user_articles.find({"user_id": user_id, "timestamps.deleted_at": None})
    user_article_list = [UserArticle(**doc) async for doc in cursor]
    
    if not user_article_list:
        return UserArticleDetailCollection(details=[])
    
    # Extract article IDs from user_article references
    article_ids = [ObjectId(ua.article_id) for ua in user_article_list]
    
    # Fetch actual articles
    articles_cursor = articles.find({"_id": {"$in": article_ids}})
    article_list = [Article(**doc) async for doc in articles_cursor]
    
    # Map articles by their id as string
    article_map = {str(article.id): article for article in article_list}
    
    details = []
    for ua in user_article_list:
        article_obj = article_map.get(str(ua.article_id))
        if article_obj:
            details.append(UserArticleDetail(article=article_obj, user_article=ua))
    
    return UserArticleDetailCollection(details=details)

async def get_user_articles_flat(user_id: str) -> UserArticleFlatCollection:
    """Get all articles saved by a user in a flattened structure (without content)"""
    # Get user's article references
    cursor = user_articles.find({"user_id": user_id, "timestamps.deleted_at": None})
    user_article_list = [UserArticle(**doc) async for doc in cursor]
    
    if not user_article_list:
        return UserArticleFlatCollection(articles=[])
    
    # Extract article IDs from user_article references
    article_ids = [ObjectId(ua.article_id) for ua in user_article_list]
    
    # Fetch actual articles without content field
    articles_cursor = articles.find({"_id": {"$in": article_ids}}, {"content": 0})
    article_list = [Article(**doc) async for doc in articles_cursor]
    
    # Map articles by their id as string
    article_map = {str(article.id): article for article in article_list}
    
    flat_articles = []
    for ua in user_article_list:
        art = article_map.get(str(ua.article_id))
        if art:
            flat_articles.append(
                UserArticleFlat(
                    **{
                        "_id": art.id,
                        "title": art.title,
                        "short_description": art.short_description,
                        "metadata": art.metadata,
                        "progress": ua.progress,
                        "timestamps": {
                            "saved_at": ua.timestamps.saved_at,
                            "archived_at": ua.timestamps.archived_at,
                            "deleted_at": ua.timestamps.deleted_at,
                            "created_at": art.created_at
                        }
                    }
                )
            )
    
    return UserArticleFlatCollection(articles=flat_articles)

async def get_user_article_flat(user_id: str, article_id: str) -> UserArticleFlat:
    """Get a specific article saved by the user in a flattened structure (always includes content)"""
    # Fetch the user_article record
    ua = await user_articles.find_one({
        "user_id": user_id,
        "article_id": ObjectId(article_id),
        "timestamps.deleted_at": None
    })
    if not ua:
        raise HTTPException(status_code=404, detail="User article not found")
    
    # Fetch the article
    art = await articles.find_one({"_id": ObjectId(article_id)})
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Convert to our models for type safety
    user_article = UserArticle(**ua)
    article = Article(**art)
    
    return UserArticleFlat(
        _id=article.id,
        title=article.title,
        content=article.content,  # Always include content for single article view
        short_description=article.short_description,
        metadata=article.metadata,
        progress=user_article.progress,
        timestamps=FlattenedTimestamps(
            saved_at=user_article.timestamps.saved_at,
            archived_at=user_article.timestamps.archived_at,
            deleted_at=user_article.timestamps.deleted_at,
            created_at=article.created_at
        )
    ) 