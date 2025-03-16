import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGODB_URL)
db = client.get_database(DATABASE_NAME)

# Collections
articles = db.get_collection("articles")
user_articles = db.get_collection("user_articles")
users = db.get_collection("users")
events = db.get_collection("events")

# Indexes setup
async def create_indexes():
    # Create indexes for better query performance
    await articles.create_index("created_at")
    
    # Create indexes for user_articles collection
    await user_articles.create_index("user_id")
    await user_articles.create_index([("user_id", 1), ("article_id", 1)], unique=True)
    await user_articles.create_index("timestamps.saved_at")
    
    # Create indexes for users collection
    await users.create_index("telegram_id", unique=True)
    await users.create_index("metadata.registered_at")
    
    # Create indexes for events collection
    await events.create_index("timestamp")
    await events.create_index("user_id")
    await events.create_index("action")