from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from logging.handlers import RotatingFileHandler
import os

from .models.article import UserArticle, UserArticleFlat, UserArticleFlatCollection
from .models.auth import AuthResponse, TelegramAuthRequest
from .services.article_service import (
    get_user_articles_flat,
    get_user_article_flat,
    update_article_progress,
    archive_user_article,
    delete_user_article
)
from .services.auth_service import authenticate_telegram_user
from .database import create_indexes

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Changed from DEBUG to INFO

# Console handler with INFO level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_format)

# Add handler to the logger
logger.addHandler(console_handler)

# Set uvicorn access logger to warning level to reduce noise
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

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