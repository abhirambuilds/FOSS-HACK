from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import models
from database import get_db

router = APIRouter(prefix="/insights", tags=["insights"])

@router.get("/{user_id}")
def get_user_insights(user_id: int, db: Session = Depends(get_db)):
    """
    Analyzes a user's recent scan history and generates personalized text insights.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    last_week = datetime.utcnow() - timedelta(days=7)
    
    # Get scans from the last 7 days
    recent_scans = db.query(models.ScanHistory).filter(
        models.ScanHistory.user_id == user_id,
        models.ScanHistory.created_at >= last_week
    ).all()

    if not recent_scans:
        return {"insights": ["Start scanning products to get personalized insights!"]}

    insights = []
    
    # Analyze Sentiments / Verdicts
    healthy_count = sum(1 for scan in recent_scans if scan.verdict == "Healthy")
    unhealthy_count = sum(1 for scan in recent_scans if scan.verdict == "Unhealthy")
    water_count = sum(1 for scan in recent_scans if scan.verdict == "Water")
    
    total_food_scans = healthy_count + unhealthy_count + sum(1 for scan in recent_scans if scan.verdict == "Moderate")

    # Insight 1: Overall Healthiness
    if total_food_scans > 0:
        healthy_ratio = healthy_count / total_food_scans
        if healthy_ratio >= 0.7:
            insights.append("🌟 Amazing! Over 70% of your recent food choices have been strictly healthy. Keep it up!")
        elif healthy_ratio >= 0.4:
            insights.append("⚖️ You have a balanced diet. Try swapping out a few unhealthy snacks for better alternatives.")
        else:
            insights.append("⚠️ Most of your recently scanned items are unhealthy. Check the app's healthy alternatives!")

    # Insight 2: Sugar & Sodium Warnings
    high_sugar_count = sum(1 for scan in recent_scans if scan.sugar_g and scan.sugar_g > 15)
    if high_sugar_count > 3:
        insights.append("🍬 Heads up! You've scanned several high-sugar items this week. Watch your sugar intake.")

    high_sodium_count = sum(1 for scan in recent_scans if scan.sodium_mg and scan.sodium_mg > 400)
    if high_sodium_count > 3:
        insights.append("🧂 You are scanning a lot of high-sodium foods. Consider reducing salty processed snacks.")

    # Insight 3: Hydration
    if water_count == 0:
        insights.append("💧 Don't forget to track your water intake! Hydration is key to a healthy lifestyle.")
    elif water_count >= 5:
        insights.append("🌊 Great job consistently tracking your hydration this week!")

    return {
        "user_id": user_id,
        "timeframe": "Last 7 days",
        "total_scans_analyzed": len(recent_scans),
        "insights": insights
    }
