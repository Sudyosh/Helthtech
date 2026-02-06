"""
Dashboard API - Psychiatrist dashboard endpoints
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import Optional

from app.database.connection import get_collection

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard():
    """
    Get comprehensive dashboard data for psychiatrists.
    Includes anonymized users, mood trends, risk scores, and alerts.
    """
    users = get_collection("users")
    mood_logs = get_collection("mood_logs")
    risk_scores = get_collection("risk_scores")
    alerts = get_collection("alerts")
    chat_logs = get_collection("chat_logs")
    
    # Get date range
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Count total users
    total_users = await users.count_documents({})
    
    # Count active users (chatted in last 7 days)
    active_users = await chat_logs.distinct("user_id", {
        "timestamp": {"$gte": week_ago}
    })
    
    # Get high risk users
    high_risk_pipeline = [
        {"$match": {"level": "HIGH", "timestamp": {"$gte": week_ago}}},
        {"$group": {"_id": "$user_id"}},
        {"$count": "count"}
    ]
    high_risk_result = await risk_scores.aggregate(high_risk_pipeline).to_list(1)
    high_risk_count = high_risk_result[0]["count"] if high_risk_result else 0
    
    # Get unresolved alerts count
    unresolved_alerts = await alerts.count_documents({"resolved": False})
    
    # Get mood trends for the week
    mood_pipeline = [
        {"$match": {"date": {"$gte": week_ago}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$date"}},
            "avg_mood": {"$avg": "$mood_score"},
            "avg_stress": {"$avg": "$stress_score"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    mood_trends = await mood_logs.aggregate(mood_pipeline).to_list(None)
    
    # Get risk level distribution
    risk_pipeline = [
        {"$match": {"timestamp": {"$gte": week_ago}}},
        {"$group": {
            "_id": "$level",
            "count": {"$sum": 1}
        }}
    ]
    risk_distribution = await risk_scores.aggregate(risk_pipeline).to_list(None)
    risk_dist_dict = {item["_id"]: item["count"] for item in risk_distribution}
    
    # Get recent alerts
    recent_alerts_cursor = alerts.find(
        {"created_at": {"$gte": week_ago}}
    ).sort("created_at", -1).limit(10)
    
    recent_alerts = []
    async for alert in recent_alerts_cursor:
        recent_alerts.append({
            "id": str(alert["_id"]),
            "user_id": alert["user_id"][:8] + "...",  # Anonymize
            "risk_level": alert["risk_level"],
            "created_at": alert["created_at"].isoformat(),
            "resolved": alert["resolved"]
        })
    
    # Get emotion distribution from chats
    emotion_pipeline = [
        {"$match": {"role": "user", "timestamp": {"$gte": week_ago}, "emotion": {"$ne": None}}},
        {"$group": {
            "_id": "$emotion",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]
    emotion_distribution = await chat_logs.aggregate(emotion_pipeline).to_list(None)
    
    return {
        "summary": {
            "total_users": total_users,
            "active_users": len(active_users),
            "high_risk_users": high_risk_count,
            "unresolved_alerts": unresolved_alerts
        },
        "mood_trends": [
            {
                "date": trend["_id"],
                "average_mood": round(trend["avg_mood"], 1),
                "average_stress": round(trend["avg_stress"], 1),
                "entries": trend["count"]
            }
            for trend in mood_trends
        ],
        "risk_distribution": {
            "LOW": risk_dist_dict.get("LOW", 0),
            "MEDIUM": risk_dist_dict.get("MEDIUM", 0),
            "HIGH": risk_dist_dict.get("HIGH", 0)
        },
        "emotion_distribution": [
            {"emotion": item["_id"], "count": item["count"]}
            for item in emotion_distribution
        ],
        "recent_alerts": recent_alerts,
        "generated_at": now.isoformat()
    }


@router.get("/dashboard/users")
async def get_dashboard_users(limit: int = 50, offset: int = 0):
    """Get list of anonymized users with their latest status."""
    users_col = get_collection("users")
    risk_scores = get_collection("risk_scores")
    mood_logs = get_collection("mood_logs")
    
    cursor = users_col.find().skip(offset).limit(limit)
    
    user_list = []
    async for user in cursor:
        user_id = user["user_id"]
        
        # Get latest risk score
        latest_risk = await risk_scores.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )
        
        # Get latest mood
        latest_mood = await mood_logs.find_one(
            {"user_id": user_id},
            sort=[("date", -1)]
        )
        
        user_list.append({
            "user_id": user_id[:8] + "...",  # Anonymize display
            "full_id": user_id,  # For internal use
            "created_at": user["created_at"].isoformat(),
            "last_active": user.get("last_active", user["created_at"]).isoformat() if user.get("last_active") else user["created_at"].isoformat(),
            "current_risk_level": latest_risk["level"] if latest_risk else "UNKNOWN",
            "latest_mood": latest_mood["mood_score"] if latest_mood else None,
            "latest_stress": latest_mood["stress_score"] if latest_mood else None
        })
    
    total = await users_col.count_documents({})
    
    return {
        "users": user_list,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/dashboard/user/{user_id}")
async def get_user_detail(user_id: str):
    """Get detailed view of a specific user (for psychiatrist review)."""
    users_col = get_collection("users")
    chat_logs = get_collection("chat_logs")
    mood_logs = get_collection("mood_logs")
    risk_scores = get_collection("risk_scores")
    
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        return {"error": "User not found"}
    
    # Get recent chat summary (last 20 messages)
    chat_cursor = chat_logs.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(20)
    
    recent_chats = []
    async for chat in chat_cursor:
        recent_chats.append({
            "role": chat["role"],
            "message": chat["message"][:100] + "..." if len(chat["message"]) > 100 else chat["message"],
            "emotion": chat.get("emotion"),
            "timestamp": chat["timestamp"].isoformat()
        })
    
    # Get mood history
    mood_cursor = mood_logs.find(
        {"user_id": user_id}
    ).sort("date", -1).limit(30)
    
    mood_history = []
    async for mood in mood_cursor:
        mood_history.append({
            "date": mood["date"].isoformat(),
            "mood_score": mood["mood_score"],
            "stress_score": mood["stress_score"]
        })
    
    # Get risk history
    risk_cursor = risk_scores.find(
        {"user_id": user_id}
    ).sort("timestamp", -1).limit(30)
    
    risk_history = []
    async for risk in risk_cursor:
        risk_history.append({
            "timestamp": risk["timestamp"].isoformat(),
            "level": risk["level"],
            "score": risk["score"],
            "factors": risk.get("factors", [])
        })
    
    return {
        "user_id": user_id[:8] + "...",
        "created_at": user["created_at"].isoformat(),
        "consent": user["consent"],
        "recent_conversations": list(reversed(recent_chats)),
        "mood_history": mood_history,
        "risk_history": risk_history
    }
