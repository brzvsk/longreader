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

# Indexes setup
async def create_indexes():
    # Create indexes for better query performance
    await articles.create_index("created_at")