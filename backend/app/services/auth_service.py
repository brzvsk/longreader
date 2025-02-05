import os
import hmac
import hashlib
import logging
from typing import Optional
from urllib.parse import unquote
import json
from fastapi import HTTPException
from ..models.user import User
from .user_service import create_user, get_user_by_telegram_id

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
logger = logging.getLogger(__name__)

def validate_init_data(init_data: str, bot_token: str) -> bool:
    """
    Validate the authentication data received from Telegram Mini App
    """
    try:
        vals = {k: unquote(v) for k, v in [s.split('=', 1) for s in init_data.split('&')]}
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash')

        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)
        
        logger.debug(f"Data check string: {data_check_string}")
        logger.debug(f"Generated hash: {h.hexdigest()}")
        logger.debug(f"Received hash: {vals['hash']}")
        
        return h.hexdigest() == vals['hash']
    except Exception as e:
        logger.error(f"Error validating init data: {e}")
        return False

async def authenticate_telegram_user(
    init_data: str,
    referral: Optional[str] = None
) -> User:
    """
    Authenticate a user from Telegram Mini App using raw initData
    """
    logger.info("Processing Telegram authentication with raw initData")
    logger.debug(f"Raw initData: {init_data}")
    
    if not BOT_TOKEN:
        logger.error("Telegram bot token not configured")
        raise HTTPException(status_code=500, detail="Telegram bot token not configured")
    
    # Validate the init data
    if not validate_init_data(init_data, BOT_TOKEN):
        logger.error("Init data validation failed")
        raise HTTPException(status_code=401, detail="Invalid authentication data")
    
    # Parse user data
    try:
        vals = dict(x.split('=', 1) for x in init_data.split('&'))
        user_data = json.loads(unquote(vals['user']))
        logger.debug(f"Parsed user data: {user_data}")
    except Exception as e:
        logger.error(f"Failed to parse user data: {e}")
        raise HTTPException(status_code=422, detail="Invalid user data format")
    
    # Get or create user using the ID from user data
    try:
        if not user_data or "id" not in user_data:
            logger.error("No user ID in auth data")
            raise HTTPException(status_code=422, detail="Missing user ID in auth data")
            
        user = await get_user_by_telegram_id(str(user_data["id"]))
        logger.info(f"Found existing user with ID: {user_data['id']}")
    except HTTPException:
        # User doesn't exist, create new one
        logger.info(f"Creating new user with ID: {user_data['id']}")
        user = await create_user(str(user_data["id"]), referral)
    
    return user 