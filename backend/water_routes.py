from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(prefix="/water", tags=["water"])

class WaterLogCreate(BaseModel):
    amount_ml: int

@router.post("/{user_id}/log")
def log_water_intake(user_id: int, payload: WaterLogCreate, db: Session = Depends(get_db)):
    """
    Logs water intake (in ml) for a user today.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.amount_ml <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # For a real system we'd use a separate table, but for the hackathon
    # let's create a special ScanHistory entry to log water intake.
    water_entry = models.ScanHistory(
        user_id=user_id,
        product_name=f"WATER_LOG",
        fat_g=payload.amount_ml, # Hack: using fat_g to store ml for this hackathon
        health_score=0,
        verdict="Water"
    )
    
    db.add(water_entry)
    db.commit()

    return {"detail": f"Logged {payload.amount_ml}ml of water"}


@router.get("/{user_id}/today")
def get_todays_water(user_id: int, db: Session = Depends(get_db)):
    """
    Returns the total water logged today by the user.
    """
    today = date.today()
    
    total_water = db.query(func.sum(models.ScanHistory.fat_g)).filter(
        models.ScanHistory.user_id == user_id,
        models.ScanHistory.verdict == "Water",
        func.date(models.ScanHistory.created_at) == today
    ).scalar()

    return {
        "user_id": user_id,
        "date": str(today),
        "total_ml": total_water or 0,
        "daily_goal_ml": 2500 # Default recommendation
    }
