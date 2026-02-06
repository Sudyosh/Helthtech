"""
Users API - User management endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from app.models.user import UserCreate, UserResponse, UserInDB
from app.database.connection import get_collection

router = APIRouter()


@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """
    Create a new anonymous user.
    Returns a unique user_id that will be used for all interactions.
    """
    users_collection = get_collection("users")
    
    user = UserInDB(
        user_id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        anonymous_mode=user_data.anonymous_mode,
        consent=user_data.consent
    )
    
    await users_collection.insert_one(user.model_dump())
    
    return UserResponse(
        user_id=user.user_id,
        created_at=user.created_at,
        anonymous_mode=user.anonymous_mode,
        consent=user.consent
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
    users_collection = get_collection("users")
    
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        user_id=user["user_id"],
        created_at=user["created_at"],
        anonymous_mode=user["anonymous_mode"],
        consent=user["consent"]
    )


@router.put("/users/{user_id}/consent")
async def update_consent(user_id: str, consent: bool):
    """Update user consent status."""
    users_collection = get_collection("users")
    
    result = await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"consent": consent}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "Consent updated", "consent": consent}
