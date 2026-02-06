"""
Mood Model - Mood and stress logging
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


class MoodLogCreate(BaseModel):
    """Request model for logging mood."""
    user_id: str
    mood_score: int = Field(..., ge=1, le=10, description="Mood score from 1-10")
    stress_score: int = Field(..., ge=1, le=10, description="Stress score from 1-10")
    notes: Optional[str] = None


class MoodLogResponse(BaseModel):
    """Response model for mood log entry."""
    id: str
    user_id: str
    mood_score: int
    stress_score: int
    notes: Optional[str]
    date: datetime
    created_at: datetime


class MoodLogInDB(BaseModel):
    """Database model for mood logs."""
    user_id: str
    mood_score: int = Field(..., ge=1, le=10)
    stress_score: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MoodHistory(BaseModel):
    """Model for mood history."""
    user_id: str
    logs: list[MoodLogResponse]
    average_mood: Optional[float] = None
    average_stress: Optional[float] = None


class StressQuestionnaire(BaseModel):
    """Stress assessment questionnaire."""
    user_id: str
    sleep_quality: int = Field(..., ge=1, le=5, description="1=Poor, 5=Excellent")
    energy_level: int = Field(..., ge=1, le=5)
    social_connection: int = Field(..., ge=1, le=5)
    anxiety_level: int = Field(..., ge=1, le=5, description="1=None, 5=Severe")
    concentration: int = Field(..., ge=1, le=5)
    physical_symptoms: Optional[str] = None
