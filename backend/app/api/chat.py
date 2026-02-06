"""
Chat API - AI Companion chat endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
import sys
import os

# Add ai_service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))

from app.models.chat import ChatMessage, ChatResponse, ChatLogInDB, ConversationHistory
from app.models.alert import AlertInDB
from app.database.connection import get_collection

router = APIRouter()


# Import AI services (with fallback for when not available)
try:
    from ai_service.emotion_classifier import classify_emotion
    from ai_service.sentiment_analyzer import analyze_sentiment
    from ai_service.risk_detector import detect_risk
    from ai_service.llm_companion import generate_response
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    
    # Fallback functions
    def classify_emotion(text):
        return {"emotion": "neutral", "confidence": 0.5}
    
    def analyze_sentiment(text):
        return {"score": 0.0, "polarity": "neutral"}
    
    def detect_risk(text, emotion=None, sentiment=None):
        return {"level": "LOW", "score": 10.0, "factors": []}
    
    async def generate_response(message, emotion=None, risk_level=None):
        return "I hear you. That sounds like something worth exploring. Would you like to tell me more about how you're feeling?"


@router.post("/chat", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """
    Send a message to the AI companion.
    Pipeline: Emotion → Sentiment → Risk → LLM Response → Save logs
    """
    chat_logs = get_collection("chat_logs")
    risk_scores = get_collection("risk_scores")
    alerts = get_collection("alerts")
    
    user_id = chat_message.user_id
    message = chat_message.message
    timestamp = datetime.utcnow()
    
    # Step 1: Emotion Classification
    emotion_result = classify_emotion(message)
    emotion = emotion_result.get("emotion", "neutral")
    emotion_confidence = emotion_result.get("confidence", 0.0)
    
    # Step 2: Sentiment Analysis
    sentiment_result = analyze_sentiment(message)
    sentiment_score = sentiment_result.get("score", 0.0)
    sentiment_polarity = sentiment_result.get("polarity", "neutral")
    
    # Step 3: Risk Detection
    risk_result = detect_risk(message, emotion=emotion, sentiment=sentiment_score)
    risk_level = risk_result.get("level", "LOW")
    risk_score = risk_result.get("score", 0.0)
    risk_factors = risk_result.get("factors", [])
    
    # Step 4: Generate AI Response
    if AI_AVAILABLE:
        ai_response = await generate_response(
            message=message,
            emotion=emotion,
            risk_level=risk_level
        )
    else:
        ai_response = await generate_response(message, emotion, risk_level)
    
    # Step 5: Save user message to logs
    user_log = ChatLogInDB(
        user_id=user_id,
        message=message,
        role="user",
        timestamp=timestamp,
        emotion=emotion,
        emotion_confidence=emotion_confidence,
        sentiment_score=sentiment_score,
        sentiment_polarity=sentiment_polarity
    )
    await chat_logs.insert_one(user_log.model_dump())
    
    # Save AI response to logs
    ai_log = ChatLogInDB(
        user_id=user_id,
        message=ai_response,
        role="ai",
        timestamp=datetime.utcnow(),
        emotion=None,
        emotion_confidence=None,
        sentiment_score=None,
        sentiment_polarity=None
    )
    await chat_logs.insert_one(ai_log.model_dump())
    
    # Save risk score
    risk_entry = {
        "user_id": user_id,
        "level": risk_level,
        "score": risk_score,
        "timestamp": timestamp,
        "factors": risk_factors,
        "trigger_message": message if risk_level in ["MEDIUM", "HIGH"] else None
    }
    await risk_scores.insert_one(risk_entry)
    
    # Create alert for HIGH risk
    if risk_level == "HIGH":
        alert = AlertInDB(
            user_id=user_id,
            risk_level=risk_level,
            trigger_message=message,
            created_at=timestamp
        )
        await alerts.insert_one(alert.model_dump())
    
    return ChatResponse(
        user_id=user_id,
        user_message=message,
        ai_response=ai_response,
        emotion=emotion,
        emotion_confidence=emotion_confidence,
        sentiment_score=sentiment_score,
        sentiment_polarity=sentiment_polarity,
        risk_level=risk_level,
        risk_score=risk_score,
        timestamp=timestamp
    )


@router.get("/chat/history/{user_id}", response_model=ConversationHistory)
async def get_chat_history(user_id: str, limit: int = 50):
    """Get conversation history for a user."""
    chat_logs = get_collection("chat_logs")
    
    cursor = chat_logs.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(limit)
    
    messages = []
    async for doc in cursor:
        messages.append(ChatLogInDB(
            user_id=doc["user_id"],
            message=doc["message"],
            role=doc["role"],
            timestamp=doc["timestamp"],
            emotion=doc.get("emotion"),
            emotion_confidence=doc.get("emotion_confidence"),
            sentiment_score=doc.get("sentiment_score"),
            sentiment_polarity=doc.get("sentiment_polarity")
        ))
    
    # Reverse to get chronological order
    messages.reverse()
    
    return ConversationHistory(
        user_id=user_id,
        messages=messages,
        total_count=len(messages)
    )
