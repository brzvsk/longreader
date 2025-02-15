from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models.article import UserArticle, UserArticleFlat, UserArticleFlatCollection
from .models.auth import AuthResponse, TelegramAuthRequest
from .services.article_service import (
    get_user_articles_flat,
    get_user_article_flat,
    update_article_progress,
    archive_user_article,
    delete_user_article,
    unarchive_user_article,
    create_share_message
)
from .services.auth_service import authenticate_telegram_user
from .database import create_indexes
from .services.parser_service import ParserService
from .services.user_service import get_user_by_telegram_id, get_user_by_id, get_or_create_by_telegram_id
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set root logger to DEBUG

# Console handler with DEBUG level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
console_handler.setFormatter(console_format)

# File handler with DEBUG level
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
file_handler.setFormatter(file_format)

# Remove any existing handlers
logger.handlers = []

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Set uvicorn access logger to warning level to reduce noise
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Create module logger
logger = logging.getLogger(__name__)
logger.info(f"Application starting at {datetime.utcnow().isoformat()}")

app = FastAPI(
    title="LongReader API",
    description="API for the LongReader application",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Initialize database indexes
    await create_indexes()

@app.get("/")
async def root():
    return {
        "message": "Welcome to LongReader API",
        "status": "running"
    }

@app.get("/users/{user_id}/articles", response_model=UserArticleFlatCollection)
async def get_articles_for_user(user_id: str):
    """Get all articles saved by a specific user in a flattened structure (without content)"""
    return await get_user_articles_flat(user_id)

@app.get("/users/{user_id}/articles/{article_id}", response_model=UserArticleFlat)
async def get_user_article(user_id: str, article_id: str):
    """Get a specific article saved by the user in a flattened structure (includes content)"""
    return await get_user_article_flat(user_id, article_id)

@app.put("/users/{user_id}/articles/{article_id}/progress", response_model=UserArticle)
async def update_progress(user_id: str, article_id: str, progress_percentage: float):
    """Update reading progress for a user's article"""
    return await update_article_progress(user_id, article_id, progress_percentage)

@app.put("/users/{user_id}/articles/{article_id}/archive", response_model=UserArticle)
async def archive_article(user_id: str, article_id: str):
    """Archive an article for a user"""
    return await archive_user_article(user_id, article_id)

@app.put("/users/{user_id}/articles/{article_id}/unarchive", response_model=UserArticle)
async def unarchive_article(user_id: str, article_id: str):
    """Unarchive an article for a user"""
    return await unarchive_user_article(user_id, article_id)

@app.delete("/users/{user_id}/articles/{article_id}", response_model=UserArticle)
async def delete_article(user_id: str, article_id: str):
    """Soft delete an article for a user"""
    return await delete_user_article(user_id, article_id)

@app.post("/auth/telegram", response_model=AuthResponse)
async def telegram_auth(auth_data: TelegramAuthRequest):
    """Authenticate user via Telegram Mini App"""
    logger = logging.getLogger(__name__)
    logger.info("Received Telegram authentication request")
    
    try:
        user = await authenticate_telegram_user(auth_data.init_data)
        logger.info(f"Successfully authenticated user with telegram_id: {user.telegram_id}")
        return AuthResponse(
            user_id=str(user.id),
            telegram_id=user.telegram_id
        )
    except HTTPException as e:
        logger.error(f"Authentication failed: {str(e.detail)}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during authentication")
        raise HTTPException(status_code=500, detail="Internal server error")

class ParseArticleRequest(BaseModel):
    url: str

@app.post("/users/{user_id}/articles/parse", response_model=dict)
async def parse_article(user_id: str, request: ParseArticleRequest, background_tasks: BackgroundTasks):
    """Parse article and create user-article link"""
    logger = logging.getLogger(__name__)
    logger.info(f"Received parse request for URL: {request.url} from user: {user_id}")
    
    try:
        # Get or create user by telegram ID
        user = await get_or_create_by_telegram_id(user_id)
        actual_user_id = str(user.id)
        
        # Create article and user article link
        logger.debug(f"Creating article and user-article link for URL: {request.url}")
        article, user_article = await ParserService.create_parsing_article(request.url, actual_user_id)
        logger.info(f"Created article {article['_id']} and user-article link {user_article['_id']}")
        
        # Start background parsing task
        logger.debug(f"Starting background parsing task for article: {article['_id']}")
        background_tasks.add_task(ParserService.parse_article, article['_id'])
        logger.info(f"Background parsing task scheduled for article: {article['_id']}")
        
        response_data = {
            "article_id": str(article['_id']),
            "user_article_id": str(user_article['_id']),
            "status": article['status'],
            "url": request.url
        }
        logger.debug(f"Returning response: {response_data}")
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to process parse request for URL: {request.url}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse article: {str(e)}"
        )

@app.post("/users/{user_id}/articles/{article_id}/share")
async def create_article_share(user_id: str, article_id: str):
    """Create a prepared inline message for sharing an article via Telegram"""
    user = await get_user_by_id(user_id)
    if not user or not user.telegram_id:
        raise HTTPException(status_code=404, detail="User not found or Telegram ID not available")
    message_id = await create_share_message(article_id, user.telegram_id)
    return {"message_id": message_id}