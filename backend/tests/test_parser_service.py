import pytest
import sys
import os
from unittest.mock import MagicMock, patch
import trafilatura
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException

# Add the parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.parser_service import ParserService
from app.models.article import Article, ArticleMetadata
from app.database import articles, user_articles

class TestParserService:
    
    def test_extract_title(self):
        """Test that title is correctly extracted from downloaded content"""
        # Create a mock downloaded object with metadata
        mock_metadata = MagicMock()
        mock_metadata.title = "Test Article Title"
        
        # Mock the trafilatura.metadata.extract_metadata function
        def mock_extract_metadata(downloaded):
            return mock_metadata
            
        # Save the original function
        original_extract_metadata = trafilatura.metadata.extract_metadata
        
        try:
            # Replace with our mock
            trafilatura.metadata.extract_metadata = mock_extract_metadata
            
            # Test 1: Extraction with raw HTML containing Open Graph title
            html_content = """
            <html>
            <head>
                <meta property="og:title" content="Open Graph Title">
                <title>HTML Title</title>
            </head>
            <body>Content</body>
            </html>
            """
            title = ParserService._extract_title(None, html_content)
            assert title == "Open Graph Title"
            
            # Test 2: Extraction with downloaded tree containing Open Graph title
            html_content = """
            <html>
            <head>
                <meta property="og:title" content="Open Graph Title from Tree">
                <title>HTML Title</title>
            </head>
            <body>Content</body>
            </html>
            """
            title = ParserService._extract_title(html_content)
            assert title == "Open Graph Title from Tree"
            
            # Test 3: Extraction with no Open Graph title, falling back to trafilatura
            html_content = """
            <html>
            <head>
                <title>HTML Title</title>
            </head>
            <body>Content</body>
            </html>
            """
            title = ParserService._extract_title(html_content)
            assert title == "Test Article Title"
            
            # Test 4: With no title at all
            mock_metadata.title = None
            title = ParserService._extract_title(html_content)
            assert title == "Untitled Article"
            
        finally:
            # Restore the original function
            trafilatura.metadata.extract_metadata = original_extract_metadata
    
    def test_strip_markdown(self):
        """Test that markdown is properly stripped from text"""
        # Test case 1: Links and images
        markdown = "Check out this [link](https://example.com) and ![image](https://example.com/image.jpg)"
        expected = "Check out this link and"
        result = ParserService._strip_markdown(markdown)
        assert result == expected
        
        # Test case 2: Headers, bold, and italic
        markdown = "# Main Header\n\n## Subheader\n\nThis is **bold** and *italic* text."
        expected = "Main Header Subheader This is bold and italic text."
        result = ParserService._strip_markdown(markdown)
        assert result == expected
        
        # Test case 3: Code blocks and inline code
        markdown = "Here is `inline code` and a code block:\n```python\nprint('hello')\n```"
        expected = "Here is inline code and a code block:"
        result = ParserService._strip_markdown(markdown)
        assert result == expected
        
        # Test case 4: Blockquotes and horizontal rules
        markdown = "> This is a quote\n\n---\n\nNormal text"
        expected = "This is a quote Normal text"
        result = ParserService._strip_markdown(markdown)
        assert result == expected
        
        # Test case 5: HTML tags
        markdown = "This has <strong>HTML</strong> tags"
        expected = "This has HTML tags"
        result = ParserService._strip_markdown(markdown)
        assert result == expected
        
        # Test case 6: Empty or None input
        assert ParserService._strip_markdown("") == ""
        assert ParserService._strip_markdown(None) == ""
    
    def test_extract_metadata(self):
        """Test that metadata is correctly extracted"""
        # Create a mock downloaded object with metadata
        mock_metadata = MagicMock()
        mock_metadata.description = "This is a **test** description with [link](https://example.com)"
        mock_metadata.author = "Test Author"
        mock_metadata.date = "2023-01-01"
        
        # Mock the trafilatura.metadata.extract_metadata function
        def mock_extract_metadata(downloaded):
            return mock_metadata
            
        # Save the original function and parse_date method
        original_extract_metadata = trafilatura.metadata.extract_metadata
        original_parse_date = ParserService._parse_date
        original_strip_markdown = ParserService._strip_markdown
        
        try:
            # Replace with our mocks
            trafilatura.metadata.extract_metadata = mock_extract_metadata
            # Use a proper datetime object instead of a string
            ParserService._parse_date = lambda date_str: datetime(2023, 1, 1) if date_str else None
            
            # Test extraction
            title = "Test Article Title"
            content = "This is the article content with some **markdown** and [links](https://example.com)."
            source_url = "https://example.com"
            
            description, article_metadata = ParserService._extract_metadata(None, content, title, source_url)
            
            # Verify markdown was stripped from description
            assert description == "This is a test description with link"
            assert article_metadata.source_url == source_url
            assert article_metadata.author == "Test Author"
            assert isinstance(article_metadata.publish_date, datetime)
            assert article_metadata.reading_time > 0
            
            # Test with no description
            mock_metadata.description = None
            description, article_metadata = ParserService._extract_metadata(None, content, title, source_url)
            # Verify markdown was stripped from content used as description
            assert description.startswith("This is the article content with some markdown and links")
            
        finally:
            # Restore the original functions
            trafilatura.metadata.extract_metadata = original_extract_metadata
            ParserService._parse_date = original_parse_date
    
    def test_remove_duplicate_title_from_content(self):
        """Test that duplicate H1 headings are removed from content when they match the title"""
        # Test case 1: H1 heading matches title exactly
        title = "Test Article Title"
        content = "# Test Article Title\n\nThis is the article content."
        result = ParserService._remove_duplicate_title(content, title, is_content=True)
        assert result == "This is the article content."
        
        # Test case 2: H1 heading matches title with different case and punctuation
        title = "Test Article Title!"
        content = "# test article title\n\nThis is the article content."
        result = ParserService._remove_duplicate_title(content, title, is_content=True)
        assert result == "This is the article content."
        
        # Test case 3: H1 heading doesn't match title
        title = "Test Article Title"
        content = "# Different Heading\n\nThis is the article content."
        result = ParserService._remove_duplicate_title(content, title, is_content=True)
        assert result == "# Different Heading\n\nThis is the article content."
        
        # Test case 4: No H1 heading
        title = "Test Article Title"
        content = "This is the article content without a heading."
        result = ParserService._remove_duplicate_title(content, title, is_content=True)
        assert result == "This is the article content without a heading."
        
        # Test case 5: H1 heading in the middle of content (should not be removed)
        title = "Test Article Title"
        content = "Intro paragraph\n\n# Test Article Title\n\nThis is the article content."
        result = ParserService._remove_duplicate_title(content, title, is_content=True)
        assert result == "Intro paragraph\n\n# Test Article Title\n\nThis is the article content."
    
    def test_remove_duplicate_title_from_description(self):
        """Test that descriptions are cleaned up when they start with the title or an H1 heading"""
        # Test case 1: Description starts with title exactly
        title = "Test Article Title"
        description = "Test Article Title - This is the article description."
        result = ParserService._remove_duplicate_title(description, title, is_content=False)
        assert result == "This is the article description."
        
        # Test case 2: Description starts with title followed by different separators
        title = "Test Article Title"
        description = "Test Article Title: This is the article description."
        result = ParserService._remove_duplicate_title(description, title, is_content=False)
        assert result == "This is the article description."
        
        # Test case 3: Description starts with H1 heading that matches title
        title = "Test Article Title"
        description = "# Test Article Title\nThis is the article description."
        result = ParserService._remove_duplicate_title(description, title, is_content=False)
        assert result == "This is the article description."
        
        # Test case 4: Description doesn't start with title or matching H1
        title = "Test Article Title"
        description = "This is the article description without a title prefix."
        result = ParserService._remove_duplicate_title(description, title, is_content=False)
        assert result == "This is the article description without a title prefix."
        
        # Test case 5: Description starts with title with different case and punctuation
        title = "Test Article Title!"
        description = "test article title - This is the article description."
        result = ParserService._remove_duplicate_title(description, title, is_content=False)
        assert result == "This is the article description."
        
        # Test case 6: Description starts with title with extra spaces and punctuation
        title = "Test Article Title"
        description = "Test  Article, Title - This is the article description."
        result = ParserService._remove_duplicate_title(description, title, is_content=False)
        assert result == "This is the article description."
    
    @pytest.mark.asyncio
    async def test_parse_url_with_og_title(self):
        """Test that parse_url correctly extracts Open Graph title and creates article and user article"""
        # Mock the _fetch_html_content method
        original_fetch_html_content = ParserService._fetch_html_content
        original_extract_title = ParserService._extract_title
        
        # Mock trafilatura functions
        original_load_html = trafilatura.load_html
        original_extract = trafilatura.extract
        original_extract_metadata = trafilatura.metadata.extract_metadata
        
        # Mock database functions
        original_find_one = articles.find_one
        original_insert_one = articles.insert_one
        original_user_articles_find_one = user_articles.find_one
        original_user_articles_insert_one = user_articles.insert_one
        
        try:
            # Create test ObjectId for user
            test_user_id = str(ObjectId())
            
            # Mock HTML content with Open Graph title
            html_content = """
            <html>
            <head>
                <meta property="og:title" content="Open Graph Title">
                <title>HTML Title</title>
            </head>
            <body>Content</body>
            </html>
            """
            
            # Mock database operations
            async def mock_articles_find_one(*args, **kwargs):
                return None  # No existing article
                
            async def mock_articles_insert_one(*args, **kwargs):
                return MagicMock(inserted_id=ObjectId())
                
            async def mock_user_articles_find_one(*args, **kwargs):
                return None  # No existing user article
                
            async def mock_user_articles_insert_one(*args, **kwargs):
                return MagicMock(inserted_id=ObjectId())
            
            # Set up mocks
            ParserService._fetch_html_content = lambda url: html_content
            ParserService._extract_title = lambda downloaded, html=None: "Open Graph Title"
            trafilatura.load_html = lambda html: html
            trafilatura.extract = lambda *args, **kwargs: "Extracted content"
            trafilatura.metadata.extract_metadata = lambda downloaded: MagicMock(
                description="Test description",
                author="Test Author",
                date="2023-01-01"
            )
            articles.find_one = mock_articles_find_one
            articles.insert_one = mock_articles_insert_one
            user_articles.find_one = mock_user_articles_find_one
            user_articles.insert_one = mock_user_articles_insert_one
            
            # Test parse_url
            result = await ParserService.parse_url("https://example.com", test_user_id)
            
            # Verify result structure
            assert "article_id" in result
            assert "user_article_id" in result
            assert isinstance(result["article_id"], str)
            assert isinstance(result["user_article_id"], str)
            
        finally:
            # Restore original functions
            ParserService._fetch_html_content = original_fetch_html_content
            ParserService._extract_title = original_extract_title
            trafilatura.load_html = original_load_html
            trafilatura.extract = original_extract
            trafilatura.metadata.extract_metadata = original_extract_metadata
            articles.find_one = original_find_one
            articles.insert_one = original_insert_one
            user_articles.find_one = original_user_articles_find_one
            user_articles.insert_one = original_user_articles_insert_one

    @pytest.mark.asyncio
    async def test_existing_url_in_database(self):
        """Test that parse_url correctly handles existing articles and creates user article relationship"""
        # Mock database functions
        original_articles_find_one = articles.find_one
        original_user_articles_find_one = user_articles.find_one
        original_user_articles_insert_one = user_articles.insert_one
        original_fetch_html_content = ParserService._fetch_html_content
        
        try:
            # Create test ObjectId for user
            test_user_id = str(ObjectId())
            
            # Create mock existing article
            mock_article_id = ObjectId()
            mock_existing_article = {
                "_id": mock_article_id,
                "title": "Existing Article",
                "content": "This is the existing article content.",
                "short_description": "Existing description",
                "metadata": {
                    "source_url": "https://example.com",
                    "author": "Test Author",
                    "publish_date": datetime(2023, 1, 1),
                    "reading_time": 1
                }
            }
            
            # Mock database operations
            async def mock_articles_find_one(*args, **kwargs):
                return mock_existing_article
                
            async def mock_user_articles_find_one(*args, **kwargs):
                return None  # No existing user article
                
            mock_user_article_id = ObjectId()
            async def mock_user_articles_insert_one(*args, **kwargs):
                return MagicMock(inserted_id=mock_user_article_id)
            
            # Set up mocks
            articles.find_one = mock_articles_find_one
            user_articles.find_one = mock_user_articles_find_one
            user_articles.insert_one = mock_user_articles_insert_one
            
            # Mock fetch_html_content to ensure it's not called
            def mock_fetch_html_content(url: str) -> str:
                raise Exception("Should not fetch HTML for existing article")
            ParserService._fetch_html_content = mock_fetch_html_content
            
            # Test parse_url with existing article
            result = await ParserService.parse_url("https://example.com", test_user_id)
            
            # Verify result structure
            assert result["article_id"] == str(mock_article_id)
            assert result["user_article_id"] == str(mock_user_article_id)
            
        finally:
            # Restore original functions
            articles.find_one = original_articles_find_one
            user_articles.find_one = original_user_articles_find_one
            user_articles.insert_one = original_user_articles_insert_one
            ParserService._fetch_html_content = original_fetch_html_content

    @pytest.mark.asyncio
    async def test_duplicate_user_article_handling(self):
        """Test that parse_url correctly handles existing user-article relationships"""
        # Mock database functions
        original_articles_find_one = articles.find_one
        original_user_articles_find_one = user_articles.find_one
        original_user_articles_insert_one = user_articles.insert_one
        original_fetch_html_content = ParserService._fetch_html_content
        
        try:
            # Create test ObjectIds
            test_user_id = str(ObjectId())
            mock_article_id = ObjectId()
            mock_user_article_id = ObjectId()
            
            # Create mock existing article and user article
            mock_existing_article = {
                "_id": mock_article_id,
                "title": "Existing Article",
                "content": "This is the existing article content.",
                "short_description": "Existing description",
                "metadata": {
                    "source_url": "https://example.com",
                    "author": "Test Author",
                    "publish_date": datetime(2023, 1, 1),
                    "reading_time": 1
                }
            }
            
            mock_existing_user_article = {
                "_id": mock_user_article_id,
                "user_id": ObjectId(test_user_id),
                "article_id": mock_article_id,
                "progress": {"percentage": 0, "last_position": 0},
                "timestamps": {"saved_at": datetime.utcnow()}
            }
            
            # Mock database operations
            async def mock_articles_find_one(*args, **kwargs):
                return mock_existing_article
                
            async def mock_user_articles_find_one(*args, **kwargs):
                return mock_existing_user_article
                
            async def mock_user_articles_insert_one(*args, **kwargs):
                raise Exception("Should not insert duplicate user article")
            
            # Set up mocks
            articles.find_one = mock_articles_find_one
            user_articles.find_one = mock_user_articles_find_one
            user_articles.insert_one = mock_user_articles_insert_one
            
            # Mock fetch_html_content to ensure it's not called
            def mock_fetch_html_content(url: str) -> str:
                raise Exception("Should not fetch HTML for existing article")
            ParserService._fetch_html_content = mock_fetch_html_content
            
            # Test parse_url with existing article and user article
            result = await ParserService.parse_url("https://example.com", test_user_id)
            
            # Verify result structure
            assert result["article_id"] == str(mock_article_id)
            assert result["user_article_id"] == str(mock_user_article_id)
            
        finally:
            # Restore original functions
            articles.find_one = original_articles_find_one
            user_articles.find_one = original_user_articles_find_one
            user_articles.insert_one = original_user_articles_insert_one
            ParserService._fetch_html_content = original_fetch_html_content

    @pytest.mark.asyncio
    async def test_daily_article_limit(self):
        """Test that daily article limit is enforced"""
        test_user_id = str(ObjectId())
        
        # Mock database functions
        original_count_documents = user_articles.count_documents
        original_find_one = articles.find_one
        
        # Mock user service
        from app.services.user_service import get_or_create_by_telegram_id
        original_get_user = get_or_create_by_telegram_id
        
        # Store original IS_DEV_ENVIRONMENT value
        original_is_dev = ParserService.IS_DEV_ENVIRONMENT
        
        try:
            # Set IS_DEV_ENVIRONMENT to False to enable limit check
            ParserService.IS_DEV_ENVIRONMENT = False
            
            # Mock count_documents to return limit reached
            async def mock_count_documents(*args, **kwargs):
                return ParserService.DAILY_ARTICLE_LIMIT
            
            # Mock articles.find_one to return an existing article
            async def mock_find_one(*args, **kwargs):
                return {"_id": ObjectId(), "metadata": {"source_url": "https://example.com"}}
            
            # Mock user service to return a user with the test ID
            async def mock_get_user(telegram_id):
                class MockUser:
                    def __init__(self):
                        self.id = ObjectId(test_user_id)
                return MockUser()
            
            # Replace functions with mocks
            user_articles.count_documents = mock_count_documents
            articles.find_one = mock_find_one
            get_or_create_by_telegram_id = mock_get_user
            
            # Test that adding one more article raises an exception
            with pytest.raises(HTTPException) as exc_info:
                await ParserService.handle_parse_request("https://example.com", test_user_id)
            
            assert exc_info.value.status_code == 429
            assert "daily article limit" in str(exc_info.value.detail).lower()
            
            # Test with count below limit
            async def mock_count_documents_below_limit(*args, **kwargs):
                return ParserService.DAILY_ARTICLE_LIMIT - 1
            
            user_articles.count_documents = mock_count_documents_below_limit
            
            # Mock user_articles.insert_one for the successful case
            original_user_articles_insert_one = user_articles.insert_one
            async def mock_user_articles_insert_one(*args, **kwargs):
                return MagicMock(inserted_id=ObjectId())
            user_articles.insert_one = mock_user_articles_insert_one
            
            # Should not raise an exception now
            await ParserService.handle_parse_request("https://example.com", test_user_id)
            
        finally:
            # Restore original functions and environment
            user_articles.count_documents = original_count_documents
            articles.find_one = original_find_one
            get_or_create_by_telegram_id = original_get_user
            ParserService.IS_DEV_ENVIRONMENT = original_is_dev
            if 'original_user_articles_insert_one' in locals():
                user_articles.insert_one = original_user_articles_insert_one

    @pytest.mark.asyncio
    async def test_error_handling_content_extraction(self):
        """Test error handling during content extraction"""
        test_user_id = str(ObjectId())
        test_url = "https://example.com"
        
        # Mock necessary functions
        original_fetch_html = ParserService._fetch_html_content
        original_extract_content = ParserService._extract_content
        original_find_one = articles.find_one
        
        try:
            # Mock database functions to return None (no existing article)
            async def mock_find_one(*args, **kwargs):
                return None
            articles.find_one = mock_find_one
            
            # Test case 1: Empty content after extraction
            def mock_fetch_html(url):
                return "<html><body>Some content</body></html>"
                
            def mock_extract_content(html_content):
                # Simulate trafilatura failing to extract content
                raise HTTPException(
                    status_code=422,
                    detail="Could not extract content from this website. The page structure may not be supported or may require JavaScript to load content."
                )
                
            ParserService._fetch_html_content = mock_fetch_html
            ParserService._extract_content = mock_extract_content
            
            with pytest.raises(HTTPException) as exc_info:
                await ParserService.parse_url(test_url, test_user_id)
            assert exc_info.value.status_code == 422
            assert "could not extract content" in str(exc_info.value.detail).lower()
            
            # Test case 2: Invalid HTML content
            def mock_fetch_html_invalid(url):
                return "Not valid HTML content"
                
            def mock_extract_content_invalid(html_content):
                # Simulate trafilatura failing to parse HTML
                raise HTTPException(
                    status_code=422,
                    detail="Could not extract content from this website. The HTML content could not be loaded."
                )
                
            ParserService._fetch_html_content = mock_fetch_html_invalid
            ParserService._extract_content = mock_extract_content_invalid
            
            with pytest.raises(HTTPException) as exc_info:
                await ParserService.parse_url(test_url, test_user_id)
            assert exc_info.value.status_code == 422
            assert "could not extract content" in str(exc_info.value.detail).lower()
            
        finally:
            # Restore original functions
            ParserService._fetch_html_content = original_fetch_html
            ParserService._extract_content = original_extract_content
            articles.find_one = original_find_one

    @pytest.mark.asyncio
    async def test_error_handling_database_operations(self):
        """Test error handling during database operations"""
        test_user_id = str(ObjectId())
        test_url = "https://example.com"
        
        # Mock necessary functions
        original_articles_find_one = articles.find_one
        original_articles_insert_one = articles.insert_one
        original_fetch_html = ParserService._fetch_html_content
        
        # Mock user service
        from app.services.user_service import get_or_create_by_telegram_id
        original_get_user = get_or_create_by_telegram_id
        
        try:
            # Mock successful HTML fetch
            def mock_fetch_html(url):
                return "<html><head><title>Test</title></head><body>Content</body></html>"
            ParserService._fetch_html_content = mock_fetch_html
            
            # Mock user service to return a user with the test ID
            async def mock_get_user(telegram_id):
                class MockUser:
                    def __init__(self):
                        self.id = ObjectId(test_user_id)
                return MockUser()
            
            get_or_create_by_telegram_id = mock_get_user
            
            # Test case 1: Database connection error during find_one
            async def mock_find_one_error(*args, **kwargs):
                raise Exception("Database connection error")
                
            articles.find_one = mock_find_one_error
            
            with pytest.raises(HTTPException) as exc_info:
                await ParserService.parse_url(test_url, test_user_id)
            assert exc_info.value.status_code == 400
            assert "database connection error" in str(exc_info.value.detail).lower()
            
            # Test case 2: Duplicate key error
            async def mock_find_one_none(*args, **kwargs):
                return None
                
            async def mock_insert_one_duplicate(*args, **kwargs):
                from pymongo.errors import DuplicateKeyError
                raise DuplicateKeyError("Duplicate key error")
                
            articles.find_one = mock_find_one_none
            articles.insert_one = mock_insert_one_duplicate
            
            with pytest.raises(HTTPException) as exc_info:
                await ParserService.parse_url(test_url, test_user_id)
            assert exc_info.value.status_code == 400
            assert "duplicate" in str(exc_info.value.detail).lower()
            
        finally:
            # Restore original functions
            articles.find_one = original_articles_find_one
            articles.insert_one = original_articles_insert_one
            ParserService._fetch_html_content = original_fetch_html
            get_or_create_by_telegram_id = original_get_user 