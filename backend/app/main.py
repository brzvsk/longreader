from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models.article import Article, ArticleContent
from .services.article_service import get_all_articles, get_article_by_id

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

@app.get("/")
async def root():
    return {
        "message": "Welcome to LongReader API",
        "status": "running"
    }

@app.get("/articles", response_model=List[Article])
async def get_articles():
    return await get_all_articles()

@app.get("/articles/{article_id}", response_model=ArticleContent)
async def get_article(article_id: str):
    return await get_article_by_id(article_id) 