from typing import List, Dict
from io import BytesIO
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

import models
from database import get_db
from auth import get_current_user
from report_generator import generate_scan_report_pdf

router = APIRouter()


@router.get("/history/{user_id}")
def get_scan_history(
    user_id: int, 
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total_count = db.query(models.ScanHistory).filter(models.ScanHistory.user_id == user_id).count()

    history = (
        db.query(models.ScanHistory)
        .filter(models.ScanHistory.user_id == user_id)
        .order_by(models.ScanHistory.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": entry.id,
                "product_name": entry.product_name,
                "health_score": entry.health_score,
                "verdict": entry.verdict,
                "created_at": entry.created_at,
            }
            for entry in history
        ]
    }


@router.get("/history/{user_id}/export")
def export_scan_history_pdf(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    history = (
        db.query(models.ScanHistory)
        .filter(models.ScanHistory.user_id == user_id)
        .order_by(models.ScanHistory.created_at.desc())
        .all()
    )

    scan_data = [
        {
            "product_name": entry.product_name,
            "health_score": entry.health_score,
            "verdict": entry.verdict,
            "created_at": entry.created_at,
            "ingredients": [
                {"name": ing.name, "flags": ing.flags}
                for ing in entry.ingredients
            ],
        }
        for entry in history
    ]

    pdf_bytes = generate_scan_report_pdf(user_id, scan_data)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=nutriscan_report_{user_id}.pdf"
        },
    )


@router.post("/history/{scan_id}/share")
def generate_share_link(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    scan = db.query(models.ScanHistory).filter(models.ScanHistory.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Generate random 10-char alphanumeric token
    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(10))

    scan.share_token = token
    db.commit()
    db.refresh(scan)

    return {"share_token": token}


@router.get("/history/shared/{token}")
def get_shared_scan(token: str, db: Session = Depends(get_db)):
    scan = db.query(models.ScanHistory).filter(models.ScanHistory.share_token == token).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Shared scan not found")

    return {
        "product_name": scan.product_name,
        "health_score": scan.health_score,
        "verdict": scan.verdict,
    }


@router.post("/history/{user_id}/sync")
def sync_scan_history(
    user_id: int,
    items: List[Dict],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    for item in items:
        nutrition = item.get("nutrition_data") or {}
        new_scan = models.ScanHistory(
            user_id=user_id,
            product_name=item.get("product_name"),
            health_score=item.get("health_score"),
            verdict=item.get("verdict"),
            calories=nutrition.get("calories"),
            fat_g=nutrition.get("fat_g"),
            sat_fat_g=nutrition.get("sat_fat_g"),
            trans_fat_g=nutrition.get("trans_fat_g"),
            sodium_mg=nutrition.get("sodium_mg"),
            carbs_g=nutrition.get("carbs_g"),
            fiber_g=nutrition.get("fiber_g"),
            sugar_g=nutrition.get("sugar_g"),
            protein_g=nutrition.get("protein_g"),
        )
        db.add(new_scan)

    db.commit()
    return {"detail": f"{len(items)} scans synced successfully"}

