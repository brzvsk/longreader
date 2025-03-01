import pytest
import re
import sys
import os
from unittest.mock import MagicMock
import trafilatura
from datetime import datetime

# Add the parent directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.parser_service import ParserService
from app.models.article import Article, ArticleMetadata

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
            
            # Test extraction
            title = ParserService._extract_title(None)  # None is fine since we're mocking
            assert title == "Test Article Title"
            
            # Test with no title
            mock_metadata.title = None
            title = ParserService._extract_title(None)
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