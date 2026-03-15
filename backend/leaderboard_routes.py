from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import models
from database import get_db

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/")
def get_global_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    """
    Returns a global leaderboard of users ranked by their total number of 'Healthy' scans.
    """
    # Count how many 'Healthy' scans each user has
    healthy_scans_query = (
        db.query(
            models.ScanHistory.user_id,
            func.count(models.ScanHistory.id).label("healthy_count")
        )
        .filter(models.ScanHistory.verdict == "Healthy")
        .group_by(models.ScanHistory.user_id)
        .subquery()
    )

    # Join with User table to get usernames
    leaderboard = (
        db.query(
            models.User.username,
            healthy_scans_query.c.healthy_count
        )
        .join(healthy_scans_query, models.User.id == healthy_scans_query.c.user_id)
        .order_by(desc(healthy_scans_query.c.healthy_count))
        .limit(limit)
        .all()
    )

    return {
        "leaderboard": [
            {"rank": idx + 1, "username": row.username, "healthy_scans": row.healthy_count}
            for idx, row in enumerate(leaderboard)
        ]
    }
