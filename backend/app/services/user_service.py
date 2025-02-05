from typing import Optional
from fastapi import HTTPException
from bson import ObjectId
from ..models.user import User
from ..database import users

async def create_user(telegram_id: str, referral: Optional[str] = None) -> User:
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await users.find_one({"telegram_id": telegram_id})
        if existing_user:
            return User(**existing_user)
        
        # Create new user
        user = User(telegram_id=telegram_id)
        if referral:
            user.metadata.referral = referral
            
        # Insert into database
        user_dict = user.model_dump(by_alias=True, exclude={"id"})  # Explicitly exclude id field
        result = await users.insert_one(user_dict)
        
        # Return created user
        created = await users.find_one({"_id": result.inserted_id})
        return User(**created)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create user")

async def get_user_by_telegram_id(telegram_id: str) -> User:
    """Get a user by their Telegram ID"""
    try:
        user = await users.find_one({"telegram_id": telegram_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**user)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

async def get_user_by_id(user_id: str) -> User:
    """Get a user by their internal ID"""
    try:
        user = await users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return User(**user)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Invalid user ID") 