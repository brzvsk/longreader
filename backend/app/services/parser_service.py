from typing import Optional, Dict, Any
import asyncio
import trafilatura
from trafilatura.settings import use_config
import httpx
from datetime import datetime
from bson import ObjectId
import logging
from fastapi import HTTPException
import random

from ..models.article import Article, ArticleMetadata
from ..database import articles, user_articles
from ..services.user_service import get_or_create_by_telegram_id

logger = logging.getLogger(__name__)

class ParserService:
    # Common modern mobile user agents
    USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Samsung SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.6261.89 Mobile/15E148 Safari/604.1"
    ]
    
    @staticmethod
    def _get_random_user_agent() -> str:
        """Return a random modern user agent string"""
        return random.choice(ParserService.USER_AGENTS)

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
    def parse_url(url: str) -> tuple[str, str, str, ArticleMetadata]:
        """Parse URL and return content with metadata"""
        logger.info(f"Starting parsing URL: {url}")
        
        try:
            # Fetch the webpage with a realistic mobile user agent
            logger.info(f"Fetching content from URL: {url}")
            headers = {
                "User-Agent": ParserService._get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                # Mobile-specific headers
                "Viewport-Width": "390",
                "Width": "390",
                "Save-Data": "on"
            }
            with httpx.Client() as client:
                response = client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                html_content = response.text
                logger.info(f"Successfully fetched URL: {url}")
            
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
                logger.error(f"Failed to extract content from URL: {url}")
                raise ValueError("Failed to extract content from URL")
            
            logger.info(f"Successfully extracted content (length: {len(content)} chars)")
            
            # Extract metadata
            title, description, article_metadata = ParserService._extract_metadata(downloaded, content, url)
            return content, title, description, article_metadata
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching URL: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch URL: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    async def handle_parse_request(url: str, user_id: str) -> dict:
        """Handle complete article parsing flow including user creation and error handling"""
        logger.info(f"Handling parse request for URL: {url} from user: {user_id}")
        try:
            # If user never opened the app before, we create a new user
            user = await get_or_create_by_telegram_id(user_id)
            actual_user_id = str(user.id)
            
            # Parse URL first
            content, title, description, article_metadata = ParserService.parse_url(url)
            
            # Create article with parsed content
            article = Article(
                title=title,
                content=content,
                short_description=description,
                metadata=article_metadata
            )
            
            # Save article to database
            result_article = await articles.insert_one(article.model_dump(by_alias=True, exclude={"id"}))
            created_article = await articles.find_one({"_id": result_article.inserted_id})
            logger.info(f"Created article with id: {created_article['_id']}")
            
            # Create user article link
            user_article_data = {
                "user_id": ObjectId(actual_user_id),
                "article_id": result_article.inserted_id,
                "progress": {"percentage": 0, "last_position": 0},
                "timestamps": {"saved_at": datetime.utcnow()}
            }
            
            result_user_article = await user_articles.insert_one(user_article_data)
            created_user_article = await user_articles.find_one({"_id": result_user_article.inserted_id})
            logger.info(f"Created user-article link with id: {created_user_article['_id']}")
            
            response_data = {
                "article_id": str(created_article['_id']),
                "user_article_id": str(created_user_article['_id']),
                "url": url
            }
            logger.debug(f"/parse returning response: {response_data}")
            return response_data
            
        except HTTPException:
            # Re-raise HTTP exceptions as is
            raise
        except Exception as e:
            logger.error(f"Failed to process parse request for URL: {url}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            ) 