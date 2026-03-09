from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
from database import get_db
from auth import get_current_user

router = APIRouter()


@router.get("/history/{user_id}")
def get_scan_history(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = (
        db.query(models.ScanHistory)
        .filter(models.ScanHistory.user_id == user_id)
        .order_by(models.ScanHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": entry.id,
            "product_name": entry.product_name,
            "health_score": entry.health_score,
            "verdict": entry.verdict,
            "created_at": entry.created_at,
        }
        for entry in history
    ]
