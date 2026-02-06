"""
Authentication API - Login, Register, Token Management
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import jwt

from app.models.auth import (
    PsychiatristRegister, PsychiatristLogin, PsychiatristInDB,
    PsychiatristResponse, Token, TokenPayload, PasswordChange
)
from app.database.connection import get_collection, settings

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = settings.secret_key
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """Hash password with SHA256 + salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        salt, stored_hash = hashed_password.split(":")
        test_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return test_hash == stored_hash
    except ValueError:
        return False


def create_access_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": email,
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token หมดอายุแล้ว กรุณาเข้าสู่ระบบใหม่"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ไม่ถูกต้อง"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PsychiatristResponse:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    psychiatrists = get_collection("psychiatrists")
    user = await psychiatrists.find_one({"email": payload.sub})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ไม่พบผู้ใช้"
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="บัญชีถูกระงับ"
        )
    
    return PsychiatristResponse(
        email=user["email"],
        full_name=user["full_name"],
        license_number=user["license_number"],
        hospital=user.get("hospital"),
        is_active=user["is_active"],
        is_verified=user.get("is_verified", False),
        created_at=user["created_at"]
    )


@router.post("/auth/register", response_model=PsychiatristResponse)
async def register(data: PsychiatristRegister):
    """Register new psychiatrist account."""
    psychiatrists = get_collection("psychiatrists")
    
    # Check if email already exists
    existing = await psychiatrists.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="อีเมลนี้มีอยู่ในระบบแล้ว"
        )
    
    # Check license number
    existing_license = await psychiatrists.find_one({"license_number": data.license_number})
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="เลขที่ใบประกอบวิชาชีพนี้มีอยู่แล้ว"
        )
    
    # Create psychiatrist
    hashed_password = hash_password(data.password)
    
    psychiatrist = PsychiatristInDB(
        email=data.email,
        hashed_password=hashed_password,
        full_name=data.full_name,
        license_number=data.license_number,
        hospital=data.hospital,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow()
    )
    
    await psychiatrists.insert_one(psychiatrist.model_dump())
    
    return PsychiatristResponse(
        email=psychiatrist.email,
        full_name=psychiatrist.full_name,
        license_number=psychiatrist.license_number,
        hospital=psychiatrist.hospital,
        is_active=psychiatrist.is_active,
        is_verified=psychiatrist.is_verified,
        created_at=psychiatrist.created_at
    )


@router.post("/auth/login", response_model=Token)
async def login(data: PsychiatristLogin):
    """Login and get JWT token."""
    psychiatrists = get_collection("psychiatrists")
    
    user = await psychiatrists.find_one({"email": data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        )
    
    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="บัญชีถูกระงับ"
        )
    
    # Update last login
    await psychiatrists.update_one(
        {"email": data.email},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token(data.email)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/auth/me", response_model=PsychiatristResponse)
async def get_me(current_user: PsychiatristResponse = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.post("/auth/logout")
async def logout(current_user: PsychiatristResponse = Depends(get_current_user)):
    """Logout (client should delete token)."""
    return {"message": "ออกจากระบบสำเร็จ"}


@router.put("/auth/password")
async def change_password(
    data: PasswordChange,
    current_user: PsychiatristResponse = Depends(get_current_user)
):
    """Change password for authenticated user."""
    psychiatrists = get_collection("psychiatrists")
    
    user = await psychiatrists.find_one({"email": current_user.email})
    
    if not verify_password(data.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="รหัสผ่านปัจจุบันไม่ถูกต้อง"
        )
    
    new_hashed = hash_password(data.new_password)
    
    await psychiatrists.update_one(
        {"email": current_user.email},
        {"$set": {"hashed_password": new_hashed}}
    )
    
    return {"message": "เปลี่ยนรหัสผ่านสำเร็จ"}


# Dependency for protected routes
async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PsychiatristResponse:
    """Dependency to require authentication."""
    return await get_current_user(credentials)
