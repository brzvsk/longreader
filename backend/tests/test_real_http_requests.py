"""
Tests for real HTTP requests to verify HTML fetching functionality.

These tests make actual network requests and should be run selectively.
They are marked with the 'real_http' marker to allow skipping during regular test runs.
"""
import pytest
import sys
import logging
from pathlib import Path
from fastapi import HTTPException
import json
import os
from bson import json_util, ObjectId

# Add the parent directory to the path so we can import our app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.parser_service import ParserService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test user ID for testing
TEST_USER_ID = str(ObjectId())

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

# URLs that are known to block scraping
BLOCKED_URLS = [
    "https://www.pcmag.com/news/14-steam-demos-from-the-game-devs-of-color-expo-you-can-play-this-weekend"
]

def save_test_results(url: str, saved_article: dict):
    """Save test results to a file for inspection."""
    os.makedirs("tests/test_data", exist_ok=True)
    filename = url.split("/")[-1][:50] + ".json"  # Limit filename length
    filepath = os.path.join("tests/test_data", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(saved_article, f, default=json_util.default, ensure_ascii=False, indent=2)

@pytest.mark.real_http
@pytest.mark.asyncio
@pytest.mark.parametrize("url", REAL_TEST_URLS)
async def test_fetch_real_html(url):
    """
    Test fetching HTML from real websites.
    
    This test makes actual HTTP requests to verify that our fetching mechanism
    works correctly with real websites.
    """
    logger.info(f"Testing real HTTP request to: {url}")
    
    try:
        # Call the parser service directly with test user ID
        saved_article = await ParserService.parse_url(url, TEST_USER_ID)
        
        # Basic assertions
        assert saved_article["article_id"] is not None, f"Failed to get article ID for {url}"
        assert saved_article["user_article_id"] is not None, f"Failed to get user article ID for {url}"
        
        # Log the results
        logger.info(f"Successfully parsed {url}")
        logger.info(f"Article ID: {saved_article['article_id']}")
        logger.info(f"User Article ID: {saved_article['user_article_id']}")
        
        # Save the parsed content for inspection
        save_test_results(url, saved_article)
        
    except HTTPException as e:
        if url in BLOCKED_URLS and e.status_code == 403:
            logger.info(f"Expected 403 error for blocked URL: {url}")
            return
        logger.error(f"Error parsing {url}: {str(e)}")
        pytest.fail(f"Failed to parse {url}: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing {url}: {str(e)}")
        pytest.fail(f"Failed to parse {url}: {str(e)}")

@pytest.mark.real_http
@pytest.mark.asyncio
async def test_error_handling_invalid_url():
    """Test error handling with an invalid URL."""
    invalid_url = "https://this-domain-does-not-exist-12345.com"
    
    with pytest.raises(HTTPException):
        await ParserService.parse_url(invalid_url, TEST_USER_ID)
    
    logger.info("Successfully caught exception for invalid URL")

@pytest.mark.real_http
@pytest.mark.asyncio
async def test_error_handling_non_html_url():
    """Test error handling with a URL that doesn't return HTML."""
    non_html_url = "https://api.github.com"
    
    with pytest.raises(HTTPException):
        await ParserService.parse_url(non_html_url, TEST_USER_ID)
    
    logger.info("Successfully caught exception for non-HTML URL") 