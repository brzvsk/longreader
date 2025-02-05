from datetime import datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Optional

PyObjectId = Annotated[str, BeforeValidator(str)]

class UserMetadata(BaseModel):
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    referral: Optional[str] = None

class User(BaseModel):
    """
    User model representing a Longreader user, primarily identified by their Telegram ID
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    telegram_id: str = Field(...)  # Using string to handle large telegram IDs safely
    metadata: UserMetadata = Field(default_factory=UserMetadata)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        exclude_unset=True,  # This will exclude None values when dumping to dict
    ) 