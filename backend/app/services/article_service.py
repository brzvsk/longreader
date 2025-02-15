from typing import List
from fastapi import HTTPException
from bson import ObjectId
from ..models.article import Article, FlattenedTimestamps, UserArticle, UserArticleFlat, UserArticleFlatCollection
from ..database import articles, user_articles
from datetime import datetime
import aiohttp
import os
import logging


async def get_user_articles_flat(user_id: str) -> UserArticleFlatCollection:
    """Get all articles saved by a user in a flattened structure (without content)"""
    # Get user's article references
    cursor = user_articles.find({"user_id": ObjectId(user_id), "timestamps.deleted_at": None})
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
        "user_id": ObjectId(user_id),
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

async def update_article_progress(user_id: str, article_id: str, progress_percentage: float) -> UserArticle:
    """Update reading progress for a user's article"""
    try:
        # Update progress
        result = await user_articles.find_one_and_update(
            {
                "user_id": ObjectId(user_id),
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
                "user_id": ObjectId(user_id),
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

async def unarchive_user_article(user_id: str, article_id: str) -> UserArticle:
    """Unarchive an article for a user"""
    try:
        result = await user_articles.find_one_and_update(
            {
                "user_id": ObjectId(user_id),
                "article_id": ObjectId(article_id),
                "timestamps.deleted_at": None
            },
            {
                "$set": {
                    "timestamps.archived_at": None
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="User article not found")
            
        return UserArticle(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to unarchive article")

async def delete_user_article(user_id: str, article_id: str) -> UserArticle:
    """Soft delete an article for a user"""
    try:
        result = await user_articles.find_one_and_update(
            {
                "user_id": ObjectId(user_id),
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

async def get_article(article_id: str) -> Article:
    """Get article by ID without user context"""
    article = await articles.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return Article(**article)

async def create_share_message(article_id: str, telegram_user_id: int) -> str:
    """Create a prepared inline message for sharing an article via Telegram"""
    logger = logging.getLogger(__name__)
    logger.info(f"Creating share message for article: {article_id} for Telegram user: {telegram_user_id}")
    
    try:
        article = await get_article(article_id)
        logger.debug(f"Found article with title: {article.title}")
        
        # Escape special characters for MarkdownV2
        header = article.title.replace('[', '\[').replace(']', '\]').replace('*', '\*').replace('_', '\_').replace('-', '\-').replace('#', '\#')
        subheader = article.short_description.replace('[', '\[').replace(']', '\]').replace('*', '\*').replace('_', '\_').replace('-', '\-').replace('#', '\#').replace('.', '\.') if article.short_description else ""
        
        # Simplify the message format to avoid markdown issues
        message_text = f"*{header}*\n\n{subheader}\n\n[Read full](https://t.me/longreader_bot/reader/{article_id})"
        logger.debug(f"Prepared message text: {message_text}")
        
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        logger.debug(f"Got bot token from env: {'Yes' if bot_token else 'No'}")
        
        if not bot_token:
            logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
            raise HTTPException(status_code=500, detail="Bot token not configured")
        
        logger.debug(f"Using bot token starting with: {bot_token[:6]}...")  # Log only first 6 chars for security
        
        async with aiohttp.ClientSession() as session:
            logger.debug("Created aiohttp session")
            bot_env = os.getenv('TELEGRAM_BOT_ENVIRONMENT', 'test')
            api_path = "test/" if bot_env == "test" else ""
            api_url = f"https://api.telegram.org/bot{bot_token}/{api_path}savePreparedInlineMessage"
            logger.debug(f"Prepared API URL (without token): https://api.telegram.org/bot.../{api_path}savePreparedInlineMessage")
            
            request_data = {
                "user_id": telegram_user_id,
                "allow_user_chats": True,
                "result": {
                    "type": "article",
                    "id": "1",  # Placeholder, not used for prepared messages
                    "title": article.title,
                    "description": article.short_description or "",
                    "input_message_content": {
                        "message_text": message_text,
                        "parse_mode": "MarkdownV2"
                    }
                }
            }
            logger.debug(f"Prepared request data: {request_data}")
            
            async with session.post(api_url, json=request_data) as response:
                logger.debug(f"Got response with status: {response.status}")
                response_text = await response.text()
                logger.debug(f"Response text: {response_text}")
                
                if response.status != 200:
                    logger.error(f"Failed to create share message. Status: {response.status}, Response: {response_text}")
                    raise HTTPException(status_code=500, detail="Failed to create share message")
                
                data = await response.json()
                message_id = data["result"]["id"]
                logger.info(f"Successfully created share message with ID: {message_id}")
                return message_id
                
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error while creating share message")
        raise HTTPException(status_code=500, detail=f"Failed to create share message: {str(e)}")