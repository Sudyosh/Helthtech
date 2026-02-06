"""
Alerts API - Alert management endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from bson import ObjectId

from app.models.alert import Alert, AlertResolve, AlertList
from app.database.connection import get_collection

router = APIRouter()


@router.get("/alerts", response_model=AlertList)
async def get_alerts(
    resolved: bool = None,
    risk_level: str = None,
    days: int = 30,
    limit: int = 50
):
    """Get alerts with optional filtering."""
    alerts = get_collection("alerts")
    
    # Build query
    query = {}
    
    if resolved is not None:
        query["resolved"] = resolved
    
    if risk_level:
        query["risk_level"] = risk_level
    
    start_date = datetime.utcnow() - timedelta(days=days)
    query["created_at"] = {"$gte": start_date}
    
    cursor = alerts.find(query).sort("created_at", -1).limit(limit)
    
    alert_list = []
    async for doc in cursor:
        alert_list.append(Alert(
            id=str(doc["_id"]),
            user_id=doc["user_id"][:8] + "...",  # Anonymize
            risk_level=doc["risk_level"],
            trigger_message=doc["trigger_message"],
            created_at=doc["created_at"],
            resolved=doc["resolved"],
            resolved_at=doc.get("resolved_at"),
            notes=doc.get("notes")
        ))
    
    # Count unresolved
    unresolved_count = await alerts.count_documents({"resolved": False})
    
    return AlertList(
        alerts=alert_list,
        total_count=len(alert_list),
        unresolved_count=unresolved_count
    )


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """Get a specific alert with full details."""
    alerts = get_collection("alerts")
    
    try:
        alert = await alerts.find_one({"_id": ObjectId(alert_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return Alert(
        id=str(alert["_id"]),
        user_id=alert["user_id"],  # Full ID for detail view
        risk_level=alert["risk_level"],
        trigger_message=alert["trigger_message"],
        created_at=alert["created_at"],
        resolved=alert["resolved"],
        resolved_at=alert.get("resolved_at"),
        notes=alert.get("notes")
    )


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, resolve_data: AlertResolve):
    """Mark an alert as resolved."""
    alerts = get_collection("alerts")
    
    try:
        result = await alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "resolved": True,
                    "resolved_at": datetime.utcnow(),
                    "notes": resolve_data.notes
                }
            }
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "message": "Alert resolved",
        "alert_id": alert_id,
        "resolved_at": datetime.utcnow().isoformat()
    }


@router.put("/alerts/{alert_id}/unresolve")
async def unresolve_alert(alert_id: str):
    """Mark an alert as unresolved (reopen)."""
    alerts = get_collection("alerts")
    
    try:
        result = await alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {
                "$set": {
                    "resolved": False,
                    "resolved_at": None
                }
            }
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID")
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "message": "Alert reopened",
        "alert_id": alert_id
    }


@router.get("/alerts/stats")
async def get_alert_stats():
    """Get alert statistics."""
    alerts = get_collection("alerts")
    
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Total counts
    total = await alerts.count_documents({})
    unresolved = await alerts.count_documents({"resolved": False})
    
    # Time-based counts
    today = await alerts.count_documents({"created_at": {"$gte": day_ago}})
    this_week = await alerts.count_documents({"created_at": {"$gte": week_ago}})
    this_month = await alerts.count_documents({"created_at": {"$gte": month_ago}})
    
    # By risk level
    by_level = {}
    for level in ["LOW", "MEDIUM", "HIGH"]:
        count = await alerts.count_documents({"risk_level": level, "resolved": False})
        by_level[level] = count
    
    return {
        "total_alerts": total,
        "unresolved_alerts": unresolved,
        "resolved_alerts": total - unresolved,
        "alerts_today": today,
        "alerts_this_week": this_week,
        "alerts_this_month": this_month,
        "unresolved_by_level": by_level
    }
