"""
Authentication Models for Psychiatrist Dashboard
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class PsychiatristRegister(BaseModel):
    """Registration request for psychiatrist."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    license_number: str  # เลขที่ใบประกอบวิชาชีพ
    hospital: Optional[str] = None


class PsychiatristLogin(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class PsychiatristInDB(BaseModel):
    """Psychiatrist stored in database."""
    email: str
    hashed_password: str
    full_name: str
    license_number: str
    hospital: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None


class PsychiatristResponse(BaseModel):
    """Psychiatrist response (without password)."""
    email: str
    full_name: str
    license_number: str
    hospital: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """JWT Token payload."""
    sub: str  # email
    exp: int  # expiration timestamp
    type: str = "access"


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(..., min_length=8)
