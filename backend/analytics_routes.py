from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta

import models
from database import get_db

router = APIRouter()


@router.get("/analytics/{user_id}/weekly")
def get_weekly_goal_summary(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = datetime.utcnow().date()
    start_date = today - timedelta(days=6)
    start_dt = datetime.combine(start_date, datetime.min.time())

    weekly_rows = (
        db.query(
            func.date(models.ScanHistory.created_at).label("scan_date"),
            func.coalesce(func.sum(models.ScanHistory.calories), 0.0).label("calories"),
            func.coalesce(func.sum(models.ScanHistory.protein_g), 0.0).label("protein_g"),
            func.coalesce(func.sum(models.ScanHistory.fat_g), 0.0).label("fat_g"),
            func.coalesce(func.sum(models.ScanHistory.carbs_g), 0.0).label("carbs_g"),
        )
        .filter(models.ScanHistory.user_id == user_id)
        .filter(models.ScanHistory.created_at >= start_dt)
        .group_by(func.date(models.ScanHistory.created_at))
        .all()
    )

    date_totals = {
        str(scan_date): {
            "calories": float(calories or 0.0),
            "protein_g": float(protein_g or 0.0),
            "fat_g": float(fat_g or 0.0),
            "carbs_g": float(carbs_g or 0.0),
        }
        for scan_date, calories, protein_g, fat_g, carbs_g in weekly_rows
    }

    last_7_days = []
    for day_offset in range(7):
        current_date = start_date + timedelta(days=day_offset)
        current_date_str = current_date.isoformat()
        totals = date_totals.get(
            current_date_str,
            {
                "calories": 0.0,
                "protein_g": 0.0,
                "fat_g": 0.0,
                "carbs_g": 0.0,
            },
        )

        last_7_days.append(
            {
                "date": current_date_str,
                "calories": totals["calories"],
                "protein_g": totals["protein_g"],
                "fat_g": totals["fat_g"],
                "carbs_g": totals["carbs_g"],
            }
        )

    return {
        "user_id": user_id,
        "target_goals": {
            "calories": float(user.target_calories or 0.0),
            "protein_g": float(user.target_protein or 0.0),
            "fat_g": float(user.target_fat or 0.0),
            "carbs_g": float(user.target_carbs or 0.0),
        },
        "last_7_days": last_7_days,
    }

@router.get("/analytics/{user_id}")
def get_user_analytics(
    user_id: int, 
    page: int = 1,
    page_size: int = 5,
    db: Session = Depends(get_db)
):
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Average health score
    avg_score = db.query(func.avg(models.ScanHistory.health_score)).filter(
        models.ScanHistory.user_id == user_id
    ).scalar()

    # 2. Count of verdicts
    verdict_counts_query = db.query(
        models.ScanHistory.verdict, 
        func.count(models.ScanHistory.id)
    ).filter(
        models.ScanHistory.user_id == user_id
    ).group_by(
        models.ScanHistory.verdict
    ).all()

    verdict_summary = {
        "Healthy": 0,
        "Moderate": 0,
        "Unhealthy": 0
    }
    
    for verdict, count in verdict_counts_query:
        # Map to known keys to ensure consistency
        v_str = str(verdict)
        verdict_summary[v_str] = count

    # 3. Top frequently encountered bad ingredients based on scans
    # Bad ingredients = health_score < 0
    
    # Total count for pagination
    total_bad_count = (
        db.query(models.IngredientData.name)
        .join(models.scan_ingredients_association, models.scan_ingredients_association.c.ingredient_id == models.IngredientData.id)
        .join(models.ScanHistory, models.ScanHistory.id == models.scan_ingredients_association.c.scan_id)
        .filter(models.ScanHistory.user_id == user_id)
        .filter(models.IngredientData.health_score < 0.0)
        .distinct()
        .count()
    )

    bad_ingredients_query = (
        db.query(
            models.IngredientData.name,
            func.count(models.scan_ingredients_association.c.scan_id).label("freq")
        )
        .join(models.scan_ingredients_association, models.scan_ingredients_association.c.ingredient_id == models.IngredientData.id)
        .join(models.ScanHistory, models.ScanHistory.id == models.scan_ingredients_association.c.scan_id)
        .filter(models.ScanHistory.user_id == user_id)
        .filter(models.IngredientData.health_score < 0.0)
        .group_by(models.IngredientData.name)
        .order_by(desc("freq"))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    top_bad_ingredients = [
        {"name": name, "count": freq}
        for name, freq in bad_ingredients_query
    ]

    return {
        "average_health_score": round(avg_score, 2) if avg_score is not None else 0.0,
        "verdict_counts": verdict_summary,
        "top_bad_ingredients": {
            "total_count": total_bad_count,
            "page": page,
            "page_size": page_size,
            "items": top_bad_ingredients
        }
    }
