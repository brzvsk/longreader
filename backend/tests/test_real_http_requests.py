"""
Tests for real HTTP requests to verify HTML fetching functionality.

These tests make actual network requests and should be run selectively.
They are marked with the 'real_http' marker to allow skipping during regular test runs.
"""
import pytest
import sys
import logging
from pathlib import Path
import httpx

# Add the parent directory to the path so we can import our app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.parser_service import ParserService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of real URLs to test
# These are URLs provided by the user for testing
REAL_TEST_URLS = [
    # PCMag article
    "https://www.pcmag.com/news/14-steam-demos-from-the-game-devs-of-color-expo-you-can-play-this-weekend",
    
    # Nature article
    "https://www.nature.com/articles/d41586-025-00437-0",
    
    # TestDouble blog post
    "https://testdouble.com/insights/product-management-restraint-why-less-delivers-more",
    
    # Russian Wikipedia article
    "https://ru.wikipedia.org/wiki/%D0%93%D0%B5%D1%80%D0%B1_%D0%9D%D0%BE%D0%B2%D0%BE%D1%81%D0%B8%D0%B1%D0%B8%D1%80%D1%81%D0%BA%D0%B0",
    
    # Substack article
    "https://aznakai.substack.com/p/the-middle-passage",
    
    # Tech blog post
    "https://lovable.dev/blog/what-no-one-talks-about-ai",
]

@pytest.mark.real_http
@pytest.mark.parametrize("url", REAL_TEST_URLS)
def test_fetch_real_html(url):
    """
    Test fetching HTML from real websites.
    
    This test makes actual HTTP requests to verify that our fetching mechanism
    works correctly with real websites.
    """
    logger.info(f"Testing real HTTP request to: {url}")
    
    try:
        # Call the parser service directly
        article = ParserService.parse_url(url)
        
        # Basic assertions
        assert article.content is not None, f"Failed to extract content from {url}"
        assert len(article.content) > 100, f"Content from {url} is too short: {len(article.content)} chars"
        assert article.title is not None, f"Failed to extract title from {url}"
        
        # Log the results
        logger.info(f"Successfully parsed {url}")
        logger.info(f"Title: {article.title}")
        logger.info(f"Content length: {len(article.content)} chars")
        logger.info(f"Metadata: {article.metadata}")
        
        # Save the HTML and parsed content for inspection
        save_test_results(url, article)
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}")
        pytest.fail(f"Failed to parse {url}: {str(e)}")

def sanitize_filename(url):
    """Create a safe filename from a URL."""
    # Remove protocol and replace special characters
    filename = url.replace('https://', '').replace('http://', '')
    filename = filename.replace('/', '_').replace('?', '_').replace('&', '_')
    filename = filename.replace('=', '_').replace('%', '_').replace('#', '_')
    return filename[:100]  # Limit length to avoid issues with long filenames

def save_test_results(url, article):
    """Save the test results for inspection."""
    # Create a directory for the results
    results_dir = Path(__file__).parent / "test_data" / "real_http_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a filename from the URL
    filename = sanitize_filename(url)
    
    # Save the parsed content
    content_path = results_dir / f"{filename}.md"
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(f"# {article.title}\n\n")
        f.write(f"URL: {url}\n\n")
        f.write(f"Description: {article.short_description}\n\n")
        f.write(f"Metadata:\n")
        f.write(f"- Source URL: {article.metadata.source_url}\n")
        f.write(f"- Author: {article.metadata.author}\n")
        f.write(f"- Publish Date: {article.metadata.publish_date}\n")
        f.write(f"- Reading Time: {article.metadata.reading_time} min\n\n")
        f.write("## Content\n\n")
        f.write(article.content)
    
    logger.info(f"Saved parsed content to {content_path}")

@pytest.mark.real_http
def test_error_handling_invalid_url():
    """Test error handling with an invalid URL."""
    invalid_url = "https://this-domain-does-not-exist-12345.com"
    
    with pytest.raises(Exception):
        ParserService.parse_url(invalid_url)
    
    logger.info("Successfully caught exception for invalid URL")

@pytest.mark.real_http
def test_error_handling_non_html_url():
    """Test error handling with a URL that doesn't return HTML."""
    # URL to a JSON API
    json_url = "https://jsonplaceholder.typicode.com/posts/1"
    
    try:
        article = ParserService.parse_url(json_url)
        # If we get here, the parser should have extracted something meaningful
        assert article.content is not None, "Parser should extract some content even from non-HTML"
        logger.info(f"Parser extracted content from JSON URL: {len(article.content)} chars")
    except Exception as e:
        # It's also acceptable if the parser raises an exception for non-HTML content
        logger.info(f"Parser raised exception for JSON URL: {str(e)}")
        pass 