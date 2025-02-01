

I'll outline how to design a Parser microservice using Trafilatura. Here's a comprehensive design:

### 1. Service Architecture

```python
# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import trafilatura
from typing import Optional, Dict, Any
import asyncio
import aiohttp
from datetime import datetime

class ParseRequest(BaseModel):
    url: HttpUrl
    options: Optional[Dict[str, Any]] = None

class ParseResponse(BaseModel):
    content: str
    metadata: Dict[str, Any]
    status: str
    parsed_at: datetime
    
app = FastAPI(title="Article Parser Service")

@app.post("/parse", response_model=ParseResponse)
async def parse_url(request: ParseRequest):
    try:
        content, metadata = await parse_article(request.url, request.options)
        return ParseResponse(
            content=content,
            metadata=metadata,
            status="success",
            parsed_at=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. Parser Implementation

```python
# app/parser.py
from typing import Tuple, Dict, Any, Optional
import trafilatura
import asyncio
import aiohttp

async def parse_article(url: str, options: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict]:
    """
    Parse article content and metadata from URL
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    # Configure parser options
    parser_config = {
        'output_format': 'markdown',
        'include_tables': True,
        'include_images': True,
        'include_links': True,
        'no_fallback': False,
    }
    
    if options:
        parser_config.update(options)

    # Extract content
    content = trafilatura.extract(
        html,
        **parser_config
    )

    # Extract metadata
    metadata = trafilatura.metadata.extract_metadata(html)

    if not content:
        raise ValueError("Failed to extract content from URL")

    return content, metadata
```

### 3. Error Handling and Validation

```python
# app/exceptions.py
from fastapi import HTTPException
from typing import Optional

class ParserException(HTTPException):
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)

class ValidationException(ParserException):
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=400)

# app/validators.py
from urllib.parse import urlparse
from typing import Optional

def validate_url(url: str) -> Optional[str]:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        raise ValidationException("Invalid URL format")
```

### 4. Caching Layer

```python
# app/cache.py
import redis
import json
from typing import Optional, Tuple, Dict

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour

    async def get_cached_content(self, url: str) -> Optional[Tuple[str, Dict]]:
        cached = self.redis.get(url)
        if cached:
            data = json.loads(cached)
            return data['content'], data['metadata']
        return None

    async def cache_content(self, url: str, content: str, metadata: Dict):
        data = {
            'content': content,
            'metadata': metadata
        }
        self.redis.setex(url, self.default_ttl, json.dumps(data))
```

### 5. Configuration and Environment

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 6. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  parser:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### 7. API Usage Example

```python
# Example client usage
import httpx

async def parse_article(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://parser-service:8000/parse",
            json={
                "url": url,
                "options": {
                    "output_format": "markdown",
                    "include_tables": True
                }
            }
        )
        return response.json()
```

### 8. Health Check and Monitoring

```python
# app/main.py
from prometheus_client import Counter, Histogram
import time

# Metrics
PARSE_TIME = Histogram('article_parse_duration_seconds', 'Time spent parsing article')
PARSE_REQUESTS = Counter('article_parse_requests_total', 'Total parse requests')

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Key Features of this Design:

1. **Scalability**
   - Stateless service design
   - Redis caching for frequently accessed content
   - Async processing for better performance

2. **Reliability**
   - Comprehensive error handling
   - Health checks
   - Monitoring metrics
   - Request validation

3. **Maintainability**
   - Modular code structure
   - Configuration management
   - Docker containerization
   - Clear API documentation

4. **Performance**
   - Caching layer
   - Async I/O
   - Configurable timeouts and limits

To deploy this service:

```bash
# Build and run
docker-compose up --build

# Scale horizontally if needed
docker-compose up --scale parser=3
```

This microservice can be easily integrated into a larger system through:
1. Direct HTTP calls
2. Message queue integration (e.g., RabbitMQ)
3. API Gateway routing
4. Service mesh configuration (e.g., Istio)
