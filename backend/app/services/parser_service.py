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
    async def parse_article(article_id: ObjectId):
        """Background task to parse the article"""
        logger.info(f"Starting parsing task for article_id: {article_id}")
        try:
            # Fetch the article to parse
            article_data = await articles.find_one({"_id": article_id})
            if not article_data:
                logger.error(f"Article not found: {article_id}")
                return
            
            article = Article(**article_data)
            source_url = article.metadata.source_url
            logger.info(f"Fetching content from URL: {source_url}")
            
            # Fetch the webpage
            async with httpx.AsyncClient() as client:
                response = await client.get(source_url)
                response.raise_for_status()
                html_content = response.text
                logger.info(f"Successfully fetched URL: {source_url} (length: {len(html_content)} bytes)")
            
            # Configure trafilatura
            config = use_config()
            config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")
            config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "100")
            
            # Enhanced configuration for better parsing
            config.set("DEFAULT", "FAVOR_PRECISION", "True")  # Prefer precision over recall
            config.set("DEFAULT", "INCLUDE_FORMATTING", "True")  # Better preserve formatting
            config.set("DEFAULT", "INCLUDE_IMAGES", "True")  # Ensure images are included
            config.set("DEFAULT", "INCLUDE_LINKS", "True")  # Ensure links are included
            config.set("DEFAULT", "INCLUDE_TABLES", "True")  # Ensure tables are included
            config.set("DEFAULT", "MIN_OUTPUT_SIZE", "100")  # Minimum output size in chars
            config.set("DEFAULT", "MAX_OUTPUT_SIZE", "0")  # No maximum size limit
            
            # Add specific handling for known blog platforms
            url_lower = source_url.lower()
            is_substack = 'substack.com' in url_lower
            is_medium = 'medium.com' in url_lower
            is_blog = any(platform in url_lower for platform in ['wordpress.com', 'blogspot.com', 'ghost.io'])
            
            if is_substack or is_medium or is_blog:
                # Use more specific selectors for blog platforms
                config.set("DEFAULT", "EXTRACTION_TIMEOUT", "60")  # Give more time for JS content
                config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "50")  # Lower threshold for blog posts
                config.set("DEFAULT", "FAVOR_RECALL", "True")  # Blogs need more recall than precision
            
            logger.debug(f"Configured trafilatura with enhanced settings for URL type: {'blog platform' if (is_substack or is_medium or is_blog) else 'general'}")
            
            # Extract content and metadata
            downloaded = trafilatura.load_html(html_content)
            logger.debug("Loaded HTML with trafilatura")
            
            # Try different extraction methods if the first one fails
            content = None
            extraction_methods = [
                # First try: Platform-specific extraction
                lambda: trafilatura.extract(
                    downloaded,
                    output_format='markdown',
                    include_tables=True,
                    include_images=True,
                    include_links=True,
                    include_formatting=True,
                    favor_precision=not (is_substack or is_medium or is_blog),  # Use recall for blogs
                    favor_recall=is_substack or is_medium or is_blog,
                    config=config
                ),
                # Second try: General extraction with precision
                lambda: trafilatura.extract(
                    downloaded,
                    output_format='markdown',
                    include_tables=True,
                    include_images=True,
                    include_links=True,
                    include_formatting=True,
                    favor_precision=True,
                    config=config
                ),
                # Last resort: Minimal settings with recall
                lambda: trafilatura.extract(
                    downloaded,
                    output_format='markdown',
                    include_images=True,
                    include_links=True,
                    favor_recall=True,
                    config=config
                )
            ]
            
            for extract_method in extraction_methods:
                try:
                    content = extract_method()
                    if content and len(content.strip()) > 100:  # Check if we got meaningful content
                        break
                except Exception as e:
                    logger.warning(f"Extraction method failed: {str(e)}")
                    continue
            
            if not content:
                logger.error(f"Failed to extract content from URL: {source_url}")
                raise ValueError("Failed to extract content from URL")
            
            # Post-process content to ensure proper formatting
            content = content.replace('\n\n\n', '\n\n')  # Remove excessive newlines
            content = content.replace('![]()', '')  # Remove empty image references
            
            # Enhanced heading formatting for blog platforms
            if is_substack or is_medium or is_blog:
                # Ensure proper spacing around headings
                for i in range(6, 0, -1):
                    heading_pattern = f"\n{'#' * i} "
                    if heading_pattern in content:
                        content = content.replace(heading_pattern, f"\n\n{'#' * i} ")
                
                # Clean up Substack-specific artifacts
                content = content.replace('Copy link', '')
                content = content.replace('Share this post', '')
                content = content.replace('More from', '')
                
                # Ensure proper list formatting
                content = content.replace('\n* ', '\n\n* ')  # Add spacing before lists
                content = content.replace('\n1. ', '\n\n1. ')  # Add spacing before numbered lists
            
            # General heading formatting
            for i in range(6, 0, -1):
                old_heading = '#' * i + ' '
                if old_heading in content:
                    content = content.replace('\n' + old_heading, '\n\n' + old_heading)
            
            logger.info(f"Successfully extracted content (length: {len(content)} chars)")
            
            # Extract metadata
            metadata = trafilatura.metadata.extract_metadata(downloaded)
            logger.debug("Extracted metadata from content")
            
            # Get title and description
            title = (metadata.title if metadata else None) or "Untitled Article"
            description = (
                metadata.description 
                if metadata and metadata.description 
                else content[:90] + "..." if content else "No description available"
            )
            
            # Calculate reading time
            word_count = len(content.split())
            reading_time = word_count // 300 + 1  # Calculate reading time in minutes
            
            # Parse publish date
            publish_date = ParserService._parse_date(metadata.date) if metadata and metadata.date else None
            logger.debug(f"Parsed publish date: {publish_date}")
            
            # Create metadata object
            article_metadata = ArticleMetadata(
                source_url=source_url,
                author=metadata.author if metadata else None,
                publish_date=publish_date,
                reading_time=reading_time
            )
            
            logger.info(f"Updating article {article_id} with parsed content")
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
                {
                    "$set": {
                        "status": ArticleStatus.FAILED,
                        "metadata.error": f"Failed to fetch URL: {str(e)}"
                    }
                }
            )
            raise
        except Exception as e:
            logger.error(f"Error parsing article {article_id}: {str(e)}", exc_info=True)
            # Update article status to failed
            await articles.update_one(
                {"_id": article_id},
                {
                    "$set": {
                        "status": ArticleStatus.FAILED,
                        "metadata.error": str(e)
                    }
                }
            )
            raise 