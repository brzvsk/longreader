from typing import Optional, Dict, Any
import asyncio
import trafilatura
from trafilatura.settings import use_config
import httpx
from datetime import datetime
from bson import ObjectId
import logging

from ..models.article import Article, ArticleStatus, UserArticle, ArticleMetadata
from ..database import articles, user_articles

logger = logging.getLogger(__name__)

class ParserService:
    @staticmethod
    async def create_parsing_article(url: str, user_id: str) -> tuple[dict, dict]:
        """Create a new article in parsing status and link it to user"""
        logger.info(f"Creating new article for URL: {url} and user_id: {user_id}")
        try:
            # Create article with minimal metadata
            article = Article(
                title="Parsing...",
                short_description="Article is being parsed...",
                metadata=ArticleMetadata(
                    source_url=url,
                    reading_time=0,  # Initial reading time
                    author=None,
                    publish_date=None
                ),
                status=ArticleStatus.PARSING
            )
            result_article = await articles.insert_one(article.model_dump(by_alias=True, exclude={"id"}))
            created_article = await articles.find_one({"_id": result_article.inserted_id})
            logger.info(f"Created article with id: {created_article['_id']}")
            
            # Create user article link with explicit ObjectId conversion
            user_article_data = {
                "user_id": ObjectId(user_id),
                "article_id": result_article.inserted_id,  # Already an ObjectId
                "progress": {"percentage": 0, "last_position": 0},
                "timestamps": {"saved_at": datetime.utcnow()}
            }
            
            result_user_article = await user_articles.insert_one(user_article_data)
            created_user_article = await user_articles.find_one({"_id": result_user_article.inserted_id})
            logger.info(f"Created user-article link with id: {created_user_article['_id']}")
            
            return created_article, created_user_article
        except Exception as e:
            logger.error(f"Failed to create article and user-article link: {str(e)}")
            raise

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        try:
            # Try parsing with different formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None
        except Exception as e:
            logger.warning(f"Failed to parse date {date_str}: {str(e)}")
            return None

    @staticmethod
    def _extract_metadata(downloaded, content: str, source_url: str) -> tuple[str, str, ArticleMetadata]:
        """Extract and process article metadata"""
        metadata = trafilatura.metadata.extract_metadata(downloaded)
        
        # Get title and description
        title = (metadata.title if metadata else None) or "Untitled Article"
        description = (
            metadata.description 
            if metadata and metadata.description 
            else content[:90] + "..." if content else "No description available"
        )
        
        # Calculate reading time (300 words per minute)
        word_count = len(content.split())
        reading_time = word_count // 300 + 1
        
        # Create metadata object
        article_metadata = ArticleMetadata(
            source_url=source_url,
            author=metadata.author if metadata else None,
            publish_date=ParserService._parse_date(metadata.date) if metadata and metadata.date else None,
            reading_time=reading_time
        )
        
        return title, description, article_metadata

    @staticmethod
    async def parse_article(article_id: ObjectId):
        """Background task to parse the article"""
        logger.info(f"Starting parsing task for article_id: {article_id}")
        try:
            # Fetch the article to parse
            article_data = await articles.find_one({"_id": article_id})
            article = Article(**article_data)
            source_url = article.metadata.source_url
            
            # Fetch the webpage
            logger.info(f"Fetching content from URL: {source_url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(source_url)
                response.raise_for_status()
                html_content = response.text
                logger.info(f"Successfully fetched URL: {source_url}")
            
            # Configure trafilatura
            config = use_config()
            config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
            config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "100")
            config.set("DEFAULT", "FAVOR_PRECISION", "True")
            config.set("DEFAULT", "INCLUDE_FORMATTING", "True")
            config.set("DEFAULT", "INCLUDE_IMAGES", "True")
            config.set("DEFAULT", "INCLUDE_LINKS", "True")
            
            # Extract content
            downloaded = trafilatura.load_html(html_content)
            content = trafilatura.extract(
                downloaded,
                output_format='markdown',
                include_images=True,
                include_links=True,
                include_formatting=True,
                favor_precision=True,
                config=config
            )
            
            if not content:
                logger.error(f"Failed to extract content from URL: {source_url}")
                raise ValueError("Failed to extract content from URL")
            
            logger.info(f"Successfully extracted content (length: {len(content)} chars)")
            
            # Extract metadata
            title, description, article_metadata = ParserService._extract_metadata(downloaded, content, source_url)
            
            # Update the article
            await articles.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "title": title,
                        "content": content,
                        "short_description": description,
                        "metadata": article_metadata.model_dump(),
                        "status": ArticleStatus.COMPLETED
                    }
                }
            )
            logger.info(f"Successfully completed parsing article {article_id}")
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching URL: {str(e)}")
            await articles.update_one(
                {"_id": article_id},
                {"$set": {"status": ArticleStatus.FAILED, "metadata.error": f"Failed to fetch URL: {str(e)}"}}
            )
            raise
        except Exception as e:
            logger.error(f"Error parsing article {article_id}: {str(e)}", exc_info=True)
            await articles.update_one(
                {"_id": article_id},
                {"$set": {"status": ArticleStatus.FAILED, "metadata.error": str(e)}}
            )
            raise 