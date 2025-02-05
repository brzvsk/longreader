from pydantic import BaseModel
from typing import Optional

class TelegramUser(BaseModel):
    """Model for Telegram user data"""
    id: int
    first_name: str
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    allows_write_to_pm: Optional[bool] = None
    photo_url: Optional[str] = None

class TelegramAuthData(BaseModel):
    """
    Model for Telegram Mini App authentication data
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    query_id: Optional[str] = None
    user: Optional[TelegramUser] = None
    auth_date: int
    hash: str
    
    # These fields are at the root level in Telegram Web App data
    id: int  # Telegram user ID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    allows_write_to_pm: Optional[bool] = None
    photo_url: Optional[str] = None
    
class AuthResponse(BaseModel):
    """Response model for successful authentication"""
    user_id: str
    telegram_id: str

class TelegramAuthRequest(BaseModel):
    """Model for raw Telegram Mini App init data"""
    init_data: str 