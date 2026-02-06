"""
MongoDB Database Connection
Uses Motor for async MongoDB operations
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings from environment variables."""
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "mental_health_companion"
    openai_api_key: str = ""
    secret_key: str = "dev-secret-key"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()


class Database:
    """Database connection manager."""
    client: Optional[AsyncIOMotorClient] = None
    db = None


db = Database()


async def connect_to_mongo():
    """Create database connection."""
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.database_name]
    
    # Create indexes for better query performance
    await db.db.users.create_index("user_id", unique=True)
    await db.db.chat_logs.create_index([("user_id", 1), ("timestamp", -1)])
    await db.db.mood_logs.create_index([("user_id", 1), ("date", -1)])
    await db.db.risk_scores.create_index([("user_id", 1), ("timestamp", -1)])
    await db.db.alerts.create_index([("created_at", -1)])
    
    print("✅ Connected to MongoDB")


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        db.client.close()
        print("🔌 Disconnected from MongoDB")


def get_database():
    """Get database instance."""
    return db.db


def get_collection(name: str):
    """Get a specific collection."""
    return db.db[name]
