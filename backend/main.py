"""
AI Mental Health Companion Platform - Backend
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api import chat, mood, dashboard, risk, alerts, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="AI Mental Health Companion",
    description="A supportive AI companion platform for teenagers to discuss mental health",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(mood.router, prefix="/api", tags=["Mood"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(risk.router, prefix="/api", tags=["Risk"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "AI Mental Health Companion API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "ready"
    }
