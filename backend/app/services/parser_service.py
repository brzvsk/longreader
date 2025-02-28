from typing import Optional, Dict, Any
import asyncio
import trafilatura
from trafilatura.settings import use_config
import httpx
from datetime import datetime, timedelta
import os
from bson import ObjectId
import logging
from fastapi import HTTPException
import random
import json
import pathlib

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
    
    # Environment check
    IS_DEV_ENVIRONMENT = os.getenv("TELEGRAM_BOT_ENVIRONMENT", "prod").lower() == "test"
    
    # Local storage paths
    LOCAL_STORAGE_DIR = pathlib.Path("./app/data/parsed_articles")
    
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
    def _fetch_html_content(url: str) -> str:
        """Fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            The HTML content as a string
            
        Raises:
            HTTPException: If there's an error fetching the content
        """
        logger.info(f"Fetching content from URL: {url}")
        try:
            # Prepare headers with a realistic mobile user agent
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
            
            # Make the HTTP request with explicit decompression
            with httpx.Client() as client:
                response = client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                # Ensure content is properly decoded
                html_content = response.text
                
                # Check if we got valid HTML content
                if not html_content or html_content.strip().startswith('\x1f\x8b'):
                    logger.warning(f"Received potentially invalid or binary HTML from {url}")
                    # Try to force decoding if needed
                    try:
                        import gzip
                        import io
                        if 'content-encoding' in response.headers and response.headers['content-encoding'] == 'gzip':
                            logger.info("Attempting manual gzip decompression")
                            decompressed = gzip.decompress(response.content)
                            html_content = decompressed.decode('utf-8')
                    except Exception as e:
                        logger.error(f"Failed to manually decompress content: {str(e)}")
                
                # Handle Brotli compression (used by Substack and other sites)
                if not html_content or (
                    'content-encoding' in response.headers and 
                    response.headers['content-encoding'] == 'br' and
                    trafilatura.load_html(html_content) is None
                ):
                    logger.info("Detected Brotli compression, attempting manual decompression")
                    try:
                        import brotli
                        decompressed = brotli.decompress(response.content)
                        html_content = decompressed.decode('utf-8')
                        logger.info("Successfully decompressed Brotli content")
                    except ImportError:
                        logger.warning("Brotli module not installed. Install with: pip install brotli")
                    except Exception as e:
                        logger.error(f"Failed to decompress Brotli content: {str(e)}")
                
                logger.info(f"Successfully fetched URL: {url}")
                
            return html_content
            
        except httpx.HTTPStatusError as e:
            # Handle specific HTTP status errors
            if e.response.status_code == 403:
                logger.error(f"Access forbidden (403) while fetching URL: {url}")
                raise HTTPException(
                    status_code=403,
                    detail=f"Website is blocking content downloading. The site may have anti-scraping measures in place."
                )
            elif e.response.status_code == 500:
                logger.error(f"Server error (500) while fetching URL: {url}")
                raise HTTPException(
                    status_code=502,  # Using 502 Bad Gateway to indicate upstream server error
                    detail=f"The website server returned an error (500). Please try again later."
                )
            else:
                logger.error(f"HTTP error while fetching URL: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch URL: {str(e)}"
                )
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching URL: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch URL: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch URL: {str(e)}"
            )

    @staticmethod
    def _create_base_filename(article: Article, article_id: str) -> tuple[pathlib.Path, str]:
        """Create storage directory and base filename for local files
        
        Args:
            article: The parsed Article object
            article_id: The ID of the article in the database
            
        Returns:
            Tuple of (storage_dir, base_filename)
        """
        # Create directory if it doesn't exist
        storage_dir = ParserService.LOCAL_STORAGE_DIR
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a safe filename from the title
        safe_title = "".join(c if c.isalnum() else "_" for c in article.title)
        safe_title = safe_title[:50]  # Limit length
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{safe_title}_{timestamp}_{article_id[:8]}"
        
        return storage_dir, base_filename

    @staticmethod
    def _save_html_file(html_content: str, article: Article, article_id: str) -> None:
        """Save original HTML content to a local file
        
        Args:
            html_content: The original HTML content
            article: The parsed Article object
            article_id: The ID of the article in the database
        """
        if not ParserService.IS_DEV_ENVIRONMENT:
            return
            
        try:
            storage_dir, base_filename = ParserService._create_base_filename(article, article_id)
            
            # Save HTML file
            html_path = storage_dir / f"{base_filename}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            logger.info(f"Saved HTML file for article {article_id}: {html_path}")
            
        except Exception as e:
            # Log error but don't fail the parsing process
            logger.error(f"Failed to save HTML file for article {article_id}: {str(e)}", exc_info=True)

    @staticmethod
    def _save_markdown_file(article: Article, article_id: str) -> None:
        """Save article content as Markdown file with metadata
        
        Args:
            article: The parsed Article object
            article_id: The ID of the article in the database
        """
        if not ParserService.IS_DEV_ENVIRONMENT:
            return
            
        try:
            storage_dir, base_filename = ParserService._create_base_filename(article, article_id)
            
            # Save MD file with metadata
            md_path = storage_dir / f"{base_filename}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                # Write metadata as YAML-like front matter
                f.write("---\n")
                f.write(f"title: {article.title}\n")
                f.write(f"source_url: {article.metadata.source_url}\n")
                if article.metadata.author:
                    f.write(f"author: {article.metadata.author}\n")
                if article.metadata.publish_date:
                    f.write(f"publish_date: {article.metadata.publish_date.isoformat()}\n")
                f.write(f"reading_time: {article.metadata.reading_time} min\n")
                f.write(f"word_count: {len(article.content.split())}\n")
                f.write(f"parsed_at: {datetime.now().isoformat()}\n")
                f.write(f"article_id: {article_id}\n")
                f.write("---\n\n")
                
                # Write content
                f.write(article.content)
                
            logger.info(f"Saved Markdown file for article {article_id}: {md_path}")
            
        except Exception as e:
            # Log error but don't fail the parsing process
            logger.error(f"Failed to save Markdown file for article {article_id}: {str(e)}", exc_info=True)

    @staticmethod
    def parse_url(url: str) -> Article:
        """Parse URL and return an Article object
        
        Args:
            url: The URL to parse
            
        Returns:
            Article: A fully populated Article object
            
        Raises:
            HTTPException: If there's an error fetching or parsing the content
        """
        
        try:
            # Fetch the HTML content
            html_content = ParserService._fetch_html_content(url)
            
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
                raise HTTPException(
                    status_code=422,  # Unprocessable Entity
                    detail="Could not extract content from this website. The page structure may not be supported or may require JavaScript to load content."
                )
            
            # Post-process content to ensure paragraphs have double newlines
            content = ParserService._ensure_paragraph_separation(content)
            
            logger.info(f"Successfully extracted content (length: {len(content)} chars)")
            
            # Extract metadata
            title, description, article_metadata = ParserService._extract_metadata(downloaded, content, url)
            
            # Create and return Article object
            article = Article(
                title=title,
                content=content,
                short_description=description,
                metadata=article_metadata
            )
            
            return article, html_content
            
        except HTTPException:
            # Re-raise HTTP exceptions as is
            raise
        except Exception as e:
            logger.error(f"Error parsing URL {url}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def _ensure_paragraph_separation(content: str) -> str:
        """Ensure paragraphs are properly separated with double newlines.
        
        Args:
            content: The markdown content extracted from the article
            
        Returns:
            Processed content with proper paragraph separation
        """
        import re
        
        # First, normalize all newlines to \n
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Replace single newlines with double newlines, but preserve existing double newlines
        # and don't affect list items, code blocks, or other markdown formatting
        
        # Step 1: Temporarily mark existing double newlines
        content = content.replace('\n\n', '§DOUBLE_NEWLINE§')
        
        # Step 2: Mark newlines that should be preserved as is (lists, code blocks, etc.)
        # Lists
        content = re.sub(r'\n([\*\-\+\d]+\. )', '§PRESERVE_NEWLINE§\\1', content)
        # Code blocks
        content = re.sub(r'\n(```|    )', '§PRESERVE_NEWLINE§\\1', content)
        # Headers
        content = re.sub(r'\n(#{1,6} )', '§PRESERVE_NEWLINE§\\1', content)
        
        # Step 3: Replace remaining single newlines with double newlines
        content = content.replace('\n', '\n\n')
        
        # Step 4: Restore preserved newlines
        content = content.replace('§PRESERVE_NEWLINE§', '\n')
        
        # Step 5: Restore original double newlines
        content = content.replace('§DOUBLE_NEWLINE§', '\n\n')
        
        # Step 6: Clean up any excessive newlines (more than 2)
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content

    # Configurable daily article limit
    DAILY_ARTICLE_LIMIT = int(os.getenv("DAILY_ARTICLE_LIMIT", 10))

    @staticmethod
    async def handle_parse_request(url: str, user_id: str) -> dict:
        """Handle complete article parsing flow including user creation and error handling"""
        logger.info(f"Handling parse request for URL: {url} from user: {user_id}")
        try:
            # If user never opened the app before, we create a new user
            user = await get_or_create_by_telegram_id(user_id)
            actual_user_id = str(user.id)
            
            # Check daily article limit
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            daily_count = await user_articles.count_documents({
                "user_id": ObjectId(actual_user_id),
                "timestamps.saved_at": {"$gte": today_start, "$lt": today_end}
            })
            if daily_count >= ParserService.DAILY_ARTICLE_LIMIT:
                logger.warning(f"User {user_id} exceeded daily article limit.")
                raise HTTPException(
                    status_code=429,
                    detail=f"Daily article limit exceeded. You can parse up to {ParserService.DAILY_ARTICLE_LIMIT} articles per day."
                )

            # Parse URL first
            article, html_content = ParserService.parse_url(url)
            
            # Save article to database
            result_article = await articles.insert_one(article.model_dump(by_alias=True, exclude={"id"}))
            article_id = str(result_article.inserted_id)
            
            # Save local files if in development environment
            if ParserService.IS_DEV_ENVIRONMENT:
                ParserService._save_html_file(html_content, article, article_id)
                ParserService._save_markdown_file(article, article_id)
            
            # Create user article link
            user_article_data = {
                "user_id": ObjectId(actual_user_id),
                "article_id": result_article.inserted_id,
                "progress": {"percentage": 0, "last_position": 0},
                "timestamps": {"saved_at": datetime.utcnow()}
            }
            
            result_user_article = await user_articles.insert_one(user_article_data)
            
            response_data = {
                "article_id": article_id,
                "user_article_id": str(result_user_article.inserted_id),
                "url": url
            }
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