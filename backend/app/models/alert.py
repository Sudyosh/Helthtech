"""
Alert Model - Risk alerts for psychiatrist dashboard
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class Alert(BaseModel):
    """Alert entry."""
    id: str
    user_id: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    trigger_message: str
    created_at: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None


class AlertCreate(BaseModel):
    """Create alert from risk detection."""
    user_id: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    trigger_message: str


class AlertInDB(BaseModel):
    """Database model for alerts."""
    user_id: str
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    trigger_message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertResolve(BaseModel):
    """Request to resolve an alert."""
    notes: Optional[str] = None


class AlertList(BaseModel):
    """List of alerts."""
    alerts: list[Alert]
    total_count: int
    unresolved_count: int
