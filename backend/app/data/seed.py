import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from bson import ObjectId
import random
import sys

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "longreader")
ENVIRONMENT = os.getenv("TELEGRAM_BOT_ENVIRONMENT", "prod")

def print_environment_error():
    print("""
ERROR: Cannot run seed script in production environment!

To run this script, you need to set the environment to 'test':

1. Add to your .env file:
   TELEGRAM_BOT_ENVIRONMENT=test

2. Or run directly with the environment variable:
   TELEGRAM_BOT_ENVIRONMENT=test python seed.py

This is a safety measure to prevent accidental data seeding in production.
""")
    sys.exit(1)

async def clear_database():
    """Clear all collections in the database without seeding new data."""
    if ENVIRONMENT == "prod":
        print_environment_error()
        
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Clear existing data
    await db.articles.delete_many({})
    await db.users.delete_many({})
    await db.user_articles.delete_many({})
    print("Database cleared successfully")

async def seed_database():
    if ENVIRONMENT == "prod":
        print_environment_error()
        
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Clear only articles and user-article links
    await db.articles.delete_many({})
    await db.user_articles.delete_many({})
    
    # Get first user from the database
    user = await db.users.find_one()
    if not user:
        print("No users found in the database. Please create a user first via opening webapp in local telegram.")
        return
    
    print(f"Using existing user with ID: {user['_id']}")
    
    # Sample articles from stub_data
    articles = [
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c69315"),
            "title": "Understanding React Server Components",
            "content": """
React Server Components represent a paradigm shift in how we build React applications. They provide a new way to think about component rendering and data fetching.

## What are Server Components?

Server Components are components that execute and render on the server. Unlike traditional React components, they never run on the client, which brings several advantages:

- Direct database access
- Reduced client-side JavaScript
- Improved initial page load

For an in-depth technical overview, check out [React Server Components RFC](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md).

## Key Benefits

### 1. Performance
Server Components can access data sources directly without additional network requests. This means faster page loads and reduced client-side processing. Learn more about performance benefits in the [official React documentation](https://react.dev/blog/2023/03/22/react-labs-what-we-have-been-working-on-march-2023#react-server-components).

### 2. Security
Sensitive operations can be performed entirely on the server, keeping API keys and other credentials secure.

### 3. Bundle Size
By executing on the server, these components don't contribute to the JavaScript bundle sent to clients. See real-world examples in [Next.js App Router documentation](https://nextjs.org/docs/app/building-your-application/rendering/server-components).

## Code Example

```jsx
async function BlogPost({ id }) {
  const post = await db.posts.findById(id);
  return <article>{post.content}</article>;
}
```

For more examples and best practices, visit the [React Server Components Patterns](https://vercel.com/blog/understanding-react-server-components).
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
            "_id": ObjectId("67b0cf9a8d22abcaf7c69316"),
            "title": "Why is React Server Components so important?",
            "content": """
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
        },
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c69317"),
            "title": "The Future of Artificial Intelligence in 2024",
            "content": """
As we delve deeper into 2024, artificial intelligence continues to reshape our world in unprecedented ways. From autonomous systems to creative AI, the landscape is evolving rapidly.

## Key Trends

### 1. Multimodal AI
Systems that can process and generate multiple types of data - text, images, audio, and video - are becoming increasingly sophisticated. Learn more about multimodal AI in [OpenAI's GPT-4V technical report](https://openai.com/research/gpt-4v-system-card).

### 2. AI Governance
The rise of AI regulation and ethical frameworks is shaping how we develop and deploy AI systems. Read about the [EU AI Act](https://www.europarl.europa.eu/news/en/headlines/society/20230601STO93804/eu-ai-act-first-regulation-on-artificial-intelligence) and its implications.

### 3. AI in Healthcare
Breakthrough applications in medical diagnosis, drug discovery, and personalized medicine. Explore [DeepMind's AlphaFold protein structure database](https://alphafold.ebi.ac.uk/) revolutionizing biological research.

## Impact on Society

The integration of AI into daily life raises important questions about privacy, employment, and human-AI collaboration. For an in-depth analysis, check out [MIT Technology Review's AI report](https://www.technologyreview.com/artificial-intelligence/).
            """,
            "short_description": "Explore the latest trends and developments in artificial intelligence and their impact on society.",
            "metadata": {
                "source_url": "https://techtrends.com/ai-future",
                "author": "Sarah Chen",
                "publish_date": datetime.utcnow() - timedelta(days=5),
                "reading_time": 12
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c69318"),
            "title": "Sustainable Architecture: Building for Tomorrow",
            "content": """
The intersection of environmental consciousness and architectural innovation is creating a new paradigm in building design.

## Core Principles

1. Energy Efficiency
2. Renewable Materials
3. Waste Reduction
4. Biophilic Design

## Innovation in Practice

Modern sustainable architecture goes beyond simple green features, incorporating smart technologies and regenerative design principles.

### Case Studies
- The Living Building Challenge
- Net-Zero Energy Buildings
- Urban Forest Integration

## Future Directions

The future of architecture lies in buildings that not only minimize environmental impact but actively contribute to ecosystem health.
            """,
            "short_description": "Discover how sustainable architecture is revolutionizing building design and urban development.",
            "metadata": {
                "source_url": "https://architectureweekly.com/sustainable",
                "author": "Michael Green",
                "publish_date": datetime.utcnow() - timedelta(days=10),
                "reading_time": 18
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c69319"),
            "title": "The Science of Deep Sleep",
            "content": """
Understanding the mechanisms of sleep is crucial for maintaining optimal health and cognitive function.

## Sleep Cycles

### The Four Stages
1. N1 (Light Sleep)
2. N2 (True Sleep)
3. N3 (Deep Sleep)
4. REM Sleep

## Impact on Health

Deep sleep plays a crucial role in:
- Memory consolidation
- Immune system function
- Cellular repair
- Emotional regulation

## Improving Sleep Quality

Evidence-based strategies for achieving better sleep, including:
- Sleep hygiene practices
- Environmental optimization
- Circadian rhythm alignment
            """,
            "short_description": "Learn about the science behind sleep cycles and how to improve your sleep quality.",
            "metadata": {
                "source_url": "https://healthscience.org/sleep",
                "author": "Dr. Emma Thompson",
                "publish_date": datetime.utcnow() - timedelta(days=3),
                "reading_time": 15
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c6931a"),
            "title": "Quantum Computing: A Beginner's Guide",
            "content": """
Quantum computing represents a fundamental shift in how we process information, leveraging quantum mechanics to solve complex problems.

## Basic Concepts

### Quantum Bits (Qubits)
Unlike classical bits, qubits can exist in multiple states simultaneously through superposition.

### Quantum Entanglement
The phenomenon that allows qubits to be fundamentally connected, regardless of distance.

## Applications

- Cryptography
- Drug Discovery
- Climate Modeling
- Financial Modeling

## Current Challenges

The field faces several obstacles:
1. Decoherence
2. Error Correction
3. Scalability

## Future Prospects

The potential impact of quantum computing on various industries and scientific research.
            """,
            "short_description": "An accessible introduction to quantum computing and its potential impact on technology.",
            "metadata": {
                "source_url": "https://quantumworld.edu/intro",
                "author": "Prof. David Quantum",
                "publish_date": datetime.utcnow() - timedelta(days=7),
                "reading_time": 20
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c69320"),
            "title": "The Complete Guide to Modern TypeScript",
            "content": """
TypeScript has evolved significantly since its inception, becoming an essential tool in modern web development. This comprehensive guide covers the latest features and best practices.

## Advanced TypeScript Features

### Type Inference
TypeScript's type inference capabilities have grown more sophisticated, allowing for better code completion and error detection.

### Template Literal Types
Learn how to leverage template literal types for more precise string manipulation and type safety.

### The satisfies Operator
Understanding the new satisfies operator and how it improves type checking without widening types.

## Best Practices

- Writing better generic constraints
- Using utility types effectively
- Pattern matching with types
            """,
            "short_description": "A comprehensive guide to TypeScript's modern features and best practices for large-scale applications.",
            "metadata": {
                "source_url": "https://www.typescriptlang.org/docs/handbook/intro.html",
                "author": "Microsoft TypeScript Team",
                "publish_date": datetime.utcnow() - timedelta(days=2),
                "reading_time": 25
            },
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId("67b0cf9a8d22abcaf7c69321"),
            "title": "The Evolution of JavaScript Frameworks in 2024",
            "content": """
As web development continues to evolve, JavaScript frameworks are adapting to new challenges and requirements. This article explores the current state of major frameworks and emerging trends.

## Current Landscape

### React's New Architecture
- Server Components
- Use Hook
- Asset Loading

### Vue's Composition API
- Script Setup
- Reactivity Transform
- Performance Improvements

### Svelte's Innovation
- Runes
- Server-side Components
- Enhanced TypeScript Support

## Future Trends
Understanding where framework development is headed and how it affects your technology choices.
            """,
            "short_description": "An in-depth look at how JavaScript frameworks are evolving and what it means for modern web development.",
            "metadata": {
                "source_url": "https://2024.stateofjs.com",
                "author": "State of JS Team",
                "publish_date": datetime.utcnow() - timedelta(days=1),
                "reading_time": 20
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert articles
    article_result = await db.articles.insert_many(articles)
    print(f"Inserted {len(article_result.inserted_ids)} articles")
    
    # Create user-article links for all articles
    user_articles = []
    base_id = "67b0d06cc899e5c6be9476"
    for i, article in enumerate(articles):
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
        
        # Generate hex string for the last two characters of ObjectId
        hex_suffix = format(i + 7, '02x')  # Convert to 2-digit hex
        
        user_articles.append({
            "_id": ObjectId(f"{base_id}{hex_suffix}"),
            "user_id": user["_id"],
            "article_id": article["_id"],
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
    print(f"Inserted {len(user_articles_result.inserted_ids)} user-article links for user {user['_id']}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        asyncio.run(clear_database())
    else:
        asyncio.run(seed_database()) 