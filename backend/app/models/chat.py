"""
Chat Model - Chat messages and AI responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """Request model for sending a chat message."""
    user_id: str
    message: str


class ChatResponse(BaseModel):
    """Response model for chat with AI analysis."""
    user_id: str
    user_message: str
    ai_response: str
    emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    sentiment_score: Optional[float] = None
    sentiment_polarity: Optional[str] = None
    risk_level: Optional[str] = None
    risk_score: Optional[float] = None
    timestamp: datetime


class ChatLogInDB(BaseModel):
    """Database model for chat logs."""
    user_id: str
    message: str
    role: Literal["user", "ai"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    emotion: Optional[str] = None
    emotion_confidence: Optional[float] = None
    sentiment_score: Optional[float] = None
    sentiment_polarity: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationHistory(BaseModel):
    """Model for conversation history."""
    user_id: str
    messages: list[ChatLogInDB]
    total_count: int
