import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "longreader")

async def seed_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Clear existing articles
    await db.articles.delete_many({})
    
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
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

## Conclusion

Server Components are changing how we think about React applications, bringing the best of server-side rendering while maintaining React's component model.
            """,
            "short_description": "A deep dive into React Server Components and how they change the way we build React applications.",
            "metadata": {
                "source_url": "https://dev.to/specific/page",
                "author": "reactdev",
                "publish_date": datetime.utcnow(),
                "reading_time": 8
            },
            "created_at": datetime.utcnow()
        },
        {
            "title": "The Future of Web Development with Next.js 15",
            "content": """
# The Future of Web Development with Next.js 15

Next.js 15 brings groundbreaking improvements to the developer experience and application performance. Let's explore what's new and how it changes web development.

## Major Improvements

### 1. Turbopack
The new Rust-based bundler promises significantly faster build times and improved development experience.

### 2. Server Actions
Built-in solution for handling form submissions and mutations without API routes.

### 3. Partial Prerendering
Combine static and dynamic content seamlessly in the same page.

## Performance Enhancements

Next.js 15 focuses heavily on performance optimizations:

- Improved static optimization
- Better code splitting
- Enhanced image optimization
- Smarter client-side caching

## Developer Experience

The developer experience has been significantly improved:

```typescript
// New API design
export default async function Page() {
  const data = await db.query()
  
  return (
    <main>
      <h1>Welcome to Next.js 15</h1>
      {data.map(item => (
        <Card key={item.id} {...item} />
      ))}
    </main>
  )
}
```

## Looking Forward

The future of web development with Next.js 15 looks promising, with more features planned for upcoming releases.
            """,
            "short_description": "Exploring the latest features and improvements in Next.js 15 and what they mean for developers.",
            "metadata": {
                "source_url": "https://medium.com/specific/page",
                "author": None,
                "publish_date": datetime.utcnow(),
                "reading_time": 12
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
    result = await db.articles.insert_many(articles)
    print(f"Inserted {len(result.inserted_ids)} articles")
    for i, article_id in enumerate(result.inserted_ids):
        print(f"Article {i + 1} ID: {article_id}")

if __name__ == "__main__":
    asyncio.run(seed_database()) 