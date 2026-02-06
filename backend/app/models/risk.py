"""
Risk Model - Risk scoring and levels
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class RiskScore(BaseModel):
    """Risk score entry."""
    user_id: str
    level: RiskLevel
    score: float = Field(..., ge=0, le=100, description="Risk score 0-100")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    factors: Optional[list[str]] = None


class RiskScoreInDB(BaseModel):
    """Database model for risk scores."""
    user_id: str
    level: RiskLevel
    score: float = Field(..., ge=0, le=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    factors: list[str] = []
    trigger_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RiskHistory(BaseModel):
    """Risk score history for a user."""
    user_id: str
    scores: list[RiskScore]
    current_level: RiskLevel
    trend: Optional[str] = None  # "improving", "stable", "worsening"


class RiskAnalysis(BaseModel):
    """Complete risk analysis result."""
    user_id: str
    overall_risk: RiskLevel
    risk_score: float
    emotion_factor: float
    sentiment_factor: float
    keyword_factor: float
    trend_factor: float
    recommendations: list[str]
