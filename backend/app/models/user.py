"""
User Model - Anonymized user representation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class UserCreate(BaseModel):
    """Request model for creating a new user."""
    anonymous_mode: bool = True
    consent: bool = True


class UserResponse(BaseModel):
    """Response model for user data."""
    user_id: str
    created_at: datetime
    anonymous_mode: bool
    consent: bool


class UserInDB(BaseModel):
    """Database model for user."""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    anonymous_mode: bool = True
    consent: bool = True
    last_active: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
