"""
Mood API - Mood and stress logging endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional

from app.models.mood import MoodLogCreate, MoodLogResponse, MoodLogInDB, MoodHistory, StressQuestionnaire
from app.database.connection import get_collection

router = APIRouter()


@router.post("/mood", response_model=MoodLogResponse)
async def log_mood(mood_data: MoodLogCreate):
    """Log a mood entry."""
    mood_logs = get_collection("mood_logs")
    
    entry = MoodLogInDB(
        user_id=mood_data.user_id,
        mood_score=mood_data.mood_score,
        stress_score=mood_data.stress_score,
        notes=mood_data.notes,
        date=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    
    result = await mood_logs.insert_one(entry.model_dump())
    
    return MoodLogResponse(
        id=str(result.inserted_id),
        user_id=entry.user_id,
        mood_score=entry.mood_score,
        stress_score=entry.stress_score,
        notes=entry.notes,
        date=entry.date,
        created_at=entry.created_at
    )


@router.get("/mood/history/{user_id}", response_model=MoodHistory)
async def get_mood_history(user_id: str, days: int = 30):
    """Get mood history for a user."""
    mood_logs = get_collection("mood_logs")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    cursor = mood_logs.find({
        "user_id": user_id,
        "date": {"$gte": start_date}
    }).sort("date", -1)
    
    logs = []
    total_mood = 0
    total_stress = 0
    count = 0
    
    async for doc in cursor:
        logs.append(MoodLogResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            mood_score=doc["mood_score"],
            stress_score=doc["stress_score"],
            notes=doc.get("notes"),
            date=doc["date"],
            created_at=doc["created_at"]
        ))
        total_mood += doc["mood_score"]
        total_stress += doc["stress_score"]
        count += 1
    
    avg_mood = total_mood / count if count > 0 else None
    avg_stress = total_stress / count if count > 0 else None
    
    return MoodHistory(
        user_id=user_id,
        logs=logs,
        average_mood=avg_mood,
        average_stress=avg_stress
    )


@router.post("/mood/questionnaire")
async def submit_stress_questionnaire(questionnaire: StressQuestionnaire):
    """Submit a stress assessment questionnaire."""
    mood_logs = get_collection("mood_logs")
    
    # Calculate derived scores
    # Higher anxiety = higher stress
    # Lower sleep/energy/concentration = higher stress
    stress_factors = [
        (5 - questionnaire.sleep_quality),
        (5 - questionnaire.energy_level),
        (5 - questionnaire.social_connection),
        questionnaire.anxiety_level,
        (5 - questionnaire.concentration)
    ]
    
    # Average stress (1-5 scale, convert to 1-10)
    avg_stress = sum(stress_factors) / len(stress_factors)
    stress_score = min(10, max(1, int(avg_stress * 2)))
    
    # Mood inversely related to stress
    mood_score = max(1, 11 - stress_score)
    
    entry = MoodLogInDB(
        user_id=questionnaire.user_id,
        mood_score=mood_score,
        stress_score=stress_score,
        notes=f"From questionnaire. Physical symptoms: {questionnaire.physical_symptoms or 'None'}",
        date=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    
    result = await mood_logs.insert_one(entry.model_dump())
    
    return {
        "id": str(result.inserted_id),
        "calculated_mood_score": mood_score,
        "calculated_stress_score": stress_score,
        "message": "Questionnaire submitted successfully"
    }


@router.get("/mood/trends/{user_id}")
async def get_mood_trends(user_id: str, days: int = 14):
    """Get mood trends grouped by day."""
    mood_logs = get_collection("mood_logs")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {
            "user_id": user_id,
            "date": {"$gte": start_date}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
            "avg_mood": {"$avg": "$mood_score"},
            "avg_stress": {"$avg": "$stress_score"},
            "entries": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    cursor = mood_logs.aggregate(pipeline)
    trends = []
    
    async for doc in cursor:
        trends.append({
            "date": doc["_id"],
            "average_mood": round(doc["avg_mood"], 1),
            "average_stress": round(doc["avg_stress"], 1),
            "entries": doc["entries"]
        })
    
    return {
        "user_id": user_id,
        "days": days,
        "trends": trends
    }
