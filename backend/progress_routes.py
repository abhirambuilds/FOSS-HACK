from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
import models
from database import get_db

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/{user_id}/today")
def get_daily_macro_progress(user_id: int, db: Session = Depends(get_db)):
    """
    Returns the user's scan totals for today vs their macro/calorie goals.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()

    # Get sum of all macros scanned today (exclude water where fat_g is used for ml)
    totals = db.query(
        func.sum(models.ScanHistory.calories).label("total_cal"),
        func.sum(models.ScanHistory.protein_g).label("total_protein"),
        func.sum(models.ScanHistory.carbs_g).label("total_carbs"),
        func.sum(models.ScanHistory.fat_g).label("total_fat"),
    ).filter(
        models.ScanHistory.user_id == user_id,
        func.date(models.ScanHistory.created_at) == today,
        models.ScanHistory.verdict != "Water"
    ).first()

    consumed = {
        "calories": totals.total_cal or 0,
        "protein_g": totals.total_protein or 0,
        "carbs_g": totals.total_carbs or 0,
        "fat_g": totals.total_fat or 0
    }

    # Use defaults if user targets are missing
    targets = {
        "calories": user.target_calories or 2000,
        "protein_g": user.target_protein or 50,
        "carbs_g": user.target_carbs or 260,
        "fat_g": user.target_fat or 70
    }

    progress = {
        k: min(100, round((consumed[k] / targets[k]) * 100, 1)) if targets[k] > 0 else 0 
        for k in consumed
    }

    return {
        "user_id": user_id,
        "date": str(today),
        "consumed": consumed,
        "targets": targets,
        "progress_percentage": progress
    }
