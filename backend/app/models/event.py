from datetime import datetime
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Optional, Any
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]

class Event(BaseModel):
    """
    Model representing an analytics event
    """
    id: Optional[PyObjectId] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str = Field(...)  # Telegram user ID
    action: str = Field(...)
    data: Any = Field(...)
    user_name: Optional[str] = None
    source: str = Field(default='(not set)')
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        exclude_unset=True,  # This will exclude None values when dumping to dict
    ) 