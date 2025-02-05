import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from bson import ObjectId
import random

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "longreader")

async def seed_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Clear existing data
    await db.articles.delete_many({})
    await db.users.delete_many({})
    await db.user_articles.delete_many({})
    
    # Sample articles from stub_data
    articles = [
        {
            "title": "Understanding React Server Components",
            "content": """
# Understanding React Server Components

React Server Components represent a paradigm shift in how we build React applications. They provide a new way to think about component rendering and data fetching.

## What are Server Components?

Server Components are components that execute and render on the server. Unlike traditional React components, they never run on the client, which brings several advantages:

- Direct database access
- Reduced client-side JavaScript
- Improved initial page load

## Key Benefits

### 1. Performance
Server Components can access data sources directly without additional network requests. This means faster page loads and reduced client-side processing.

### 2. Security
Sensitive operations can be performed entirely on the server, keeping API keys and other credentials secure.

### 3. Bundle Size
By executing on the server, these components don't contribute to the JavaScript bundle sent to clients.

## Code Example

```jsx
async function BlogPost({ id }) {
  const post = await db.posts.findById(id);
  return <article>{post.content}</article>;
}
```
            """,
            "short_description": "Learn about React Server Components and how they change the way we build React applications.",
            "metadata": {
                "source_url": "https://example.com/react-server-components",
                "author": "John Doe",
                "publish_date": datetime.utcnow(),
                "reading_time": 10
            },
            "created_at": datetime.utcnow()
        },
        {
            "title": "Why is React Server Components so important?",
            "content": """
# Why React Server Components Matter

React Server Components are revolutionizing how we build modern web applications. This article explores their significance and impact on web development.

## The Problem They Solve

Traditional React applications face several challenges:
1. Large JavaScript bundles
2. Complex data fetching patterns
3. Security concerns with sensitive data

React Server Components address these issues head-on.

## Key Advantages

- Zero bundle size impact
- Direct backend access
- Improved security
- Better performance

## Real-world Impact

Server Components are already making waves in production applications, showing significant improvements in various metrics.
            """,
            "short_description": "React Server Components are a new way to build React applications that are faster, more secure, and easier to scale.",
            "metadata": {
                "source_url": "https://dev.to/specific/page",
                "author": None,
                "publish_date": datetime.utcnow(),
                "reading_time": 15
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert articles
    article_result = await db.articles.insert_many(articles)
    print(f"Inserted {len(article_result.inserted_ids)} articles")
    
    # Create test user
    test_user = {
        "telegram_id": "123456789",
        "metadata": {
            "registered_at": datetime.utcnow(),
            "referral": "test_referral"
        }
    }
    
    # Insert test user
    user_result = await db.users.insert_one(test_user)
    print(f"Inserted test user with ID: {user_result.inserted_id}")
    
    # Create user-article links for all articles
    user_articles = []
    for article, article_id in zip(articles, article_result.inserted_ids):
        content_length = len(article["content"])
        percentage = random.randint(0, 100)
        last_position = int(content_length * (percentage / 100))
        
        # Generate random datetime for saved_at
        random_days_saved = random.randint(0, 30)
        random_seconds_saved = random.randint(0, 86400)
        saved_at = datetime.utcnow() - timedelta(days=random_days_saved, seconds=random_seconds_saved)
        
        # Generate random datetime for updated_at, ensuring it's later than saved_at
        random_days_updated = random.randint(0, 30 - random_days_saved)
        random_seconds_updated = random.randint(0, 86400 - random_seconds_saved)
        updated_at = saved_at + timedelta(days=random_days_updated, seconds=random_seconds_updated)
        
        user_articles.append({
            "user_id": str(user_result.inserted_id),
            "article_id": article_id,
            "progress": {
                "percentage": percentage,
                "last_position": last_position,
                "updated_at": updated_at
            },
            "timestamps": {
                "saved_at": saved_at,
                "archived_at": None,
                "deleted_at": None
            }
        })
    
    # Insert user-article links
    user_articles_result = await db.user_articles.insert_many(user_articles)
    print(f"Inserted {len(user_articles_result.inserted_ids)} user-article links")

if __name__ == "__main__":
    asyncio.run(seed_database()) 