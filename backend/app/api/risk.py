"""
Risk API - Risk score endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional

from app.models.risk import RiskScore, RiskHistory, RiskAnalysis
from app.database.connection import get_collection

router = APIRouter()


@router.get("/risk/{user_id}")
async def get_risk_scores(user_id: str, days: int = 30):
    """Get risk score history for a user."""
    risk_scores = get_collection("risk_scores")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    cursor = risk_scores.find({
        "user_id": user_id,
        "timestamp": {"$gte": start_date}
    }).sort("timestamp", -1)
    
    scores = []
    async for doc in cursor:
        scores.append(RiskScore(
            user_id=doc["user_id"],
            level=doc["level"],
            score=doc["score"],
            timestamp=doc["timestamp"],
            factors=doc.get("factors")
        ))
    
    # Determine current level (most recent)
    current_level = scores[0].level if scores else "LOW"
    
    # Determine trend
    if len(scores) >= 5:
        recent_avg = sum(s.score for s in scores[:5]) / 5
        older_avg = sum(s.score for s in scores[5:10]) / min(5, len(scores[5:10])) if len(scores) > 5 else recent_avg
        
        if recent_avg < older_avg - 5:
            trend = "improving"
        elif recent_avg > older_avg + 5:
            trend = "worsening"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return RiskHistory(
        user_id=user_id,
        scores=scores,
        current_level=current_level,
        trend=trend
    )


@router.get("/risk/{user_id}/analysis")
async def get_risk_analysis(user_id: str):
    """Get comprehensive risk analysis for a user."""
    risk_scores = get_collection("risk_scores")
    mood_logs = get_collection("mood_logs")
    chat_logs = get_collection("chat_logs")
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get recent risk scores
    risk_cursor = risk_scores.find({
        "user_id": user_id,
        "timestamp": {"$gte": week_ago}
    }).sort("timestamp", -1)
    
    risks = []
    total_score = 0
    async for doc in risk_cursor:
        risks.append(doc)
        total_score += doc["score"]
    
    avg_risk_score = total_score / len(risks) if risks else 0
    
    # Get mood data
    mood_cursor = mood_logs.find({
        "user_id": user_id,
        "date": {"$gte": week_ago}
    })
    
    total_mood = 0
    total_stress = 0
    mood_count = 0
    async for mood in mood_cursor:
        total_mood += mood["mood_score"]
        total_stress += mood["stress_score"]
        mood_count += 1
    
    avg_mood = total_mood / mood_count if mood_count else 5
    avg_stress = total_stress / mood_count if mood_count else 5
    
    # Get emotion data
    emotion_cursor = chat_logs.find({
        "user_id": user_id,
        "role": "user",
        "timestamp": {"$gte": week_ago},
        "emotion": {"$ne": None}
    })
    
    negative_emotions = ["sadness", "fear", "anger", "disgust"]
    negative_count = 0
    total_emotions = 0
    
    async for chat in emotion_cursor:
        total_emotions += 1
        if chat.get("emotion") in negative_emotions:
            negative_count += 1
    
    negative_ratio = negative_count / total_emotions if total_emotions else 0
    
    # Calculate component factors
    emotion_factor = min(100, negative_ratio * 100 * 1.5)  # Up to 100
    sentiment_factor = min(100, avg_stress * 10)  # Stress 1-10 → 10-100
    keyword_factor = max(r["score"] for r in risks) if risks else 0
    trend_factor = 50  # Neutral baseline
    
    # Overall risk
    overall_score = (emotion_factor * 0.2 + sentiment_factor * 0.2 + 
                     keyword_factor * 0.4 + (100 - avg_mood * 10) * 0.2)
    
    if overall_score >= 70:
        overall_risk = "HIGH"
    elif overall_score >= 40:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"
    
    # Generate recommendations
    recommendations = []
    if overall_risk == "HIGH":
        recommendations.append("Immediate professional review recommended")
        recommendations.append("Consider reaching out to the user directly")
    if avg_stress > 7:
        recommendations.append("High stress levels detected - suggest stress management resources")
    if negative_ratio > 0.6:
        recommendations.append("Frequent negative emotions - consider mood intervention")
    if not recommendations:
        recommendations.append("Continue monitoring - no immediate concerns")
    
    return RiskAnalysis(
        user_id=user_id,
        overall_risk=overall_risk,
        risk_score=round(overall_score, 1),
        emotion_factor=round(emotion_factor, 1),
        sentiment_factor=round(sentiment_factor, 1),
        keyword_factor=round(keyword_factor, 1),
        trend_factor=round(trend_factor, 1),
        recommendations=recommendations
    )


@router.get("/risk/high-risk-users")
async def get_high_risk_users(days: int = 7):
    """Get list of users with HIGH risk in recent period."""
    risk_scores = get_collection("risk_scores")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {
            "level": "HIGH",
            "timestamp": {"$gte": start_date}
        }},
        {"$group": {
            "_id": "$user_id",
            "high_risk_count": {"$sum": 1},
            "latest": {"$max": "$timestamp"},
            "max_score": {"$max": "$score"}
        }},
        {"$sort": {"max_score": -1}}
    ]
    
    cursor = risk_scores.aggregate(pipeline)
    
    users = []
    async for doc in cursor:
        users.append({
            "user_id": doc["_id"][:8] + "...",
            "full_id": doc["_id"],
            "high_risk_occurrences": doc["high_risk_count"],
            "latest_occurrence": doc["latest"].isoformat(),
            "max_score": doc["max_score"]
        })
    
    return {
        "high_risk_users": users,
        "total": len(users),
        "period_days": days
    }
