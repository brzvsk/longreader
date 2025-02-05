from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.article import UserArticle, UserArticleFlat, UserArticleFlatCollection
from .services.article_service import (
    get_user_articles_flat,
    get_user_article_flat,
    update_article_progress,
    archive_user_article,
    delete_user_article
)
from .database import create_indexes

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