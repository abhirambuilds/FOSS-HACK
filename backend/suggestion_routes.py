from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

import models
from database import get_db

router = APIRouter()


def get_healthy_alternatives(db: Session, bad_ingredient: Optional[str] = None, limit: int = 3) -> list:
    """
    Returns a list of healthy ingredient alternatives.
    Queries IngredientData table for items with a high health_score (>= 0.5)
    that don't share the same name as the bad_ingredient.
    """
    query = db.query(models.IngredientData).filter(models.IngredientData.health_score >= 0.5)

    if bad_ingredient:
        query = query.filter(~models.IngredientData.name.ilike(f"%{bad_ingredient}%"))

    alternatives = query.order_by(models.IngredientData.health_score.desc()).limit(limit).all()

    return [
        {"name": item.name, "health_score": item.health_score, "flags": item.flags}
        for item in alternatives
    ]


@router.get("/alternatives")
def suggest_alternatives(
    bad_ingredient: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns up to 3 healthier ingredient alternatives.
    Optionally pass `bad_ingredient` to avoid it in results.
    """
    results = get_healthy_alternatives(db, bad_ingredient=bad_ingredient)
    return {"alternatives": results}


@router.get("/ingredients/search")
def search_ingredients(
    name: Optional[str] = None,
    flag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search the ingredients database by name or flag.
    e.g. /api/ingredients/search?name=sugar
    e.g. /api/ingredients/search?flag=vegan
    """
    query = db.query(models.IngredientData)

    if name:
        query = query.filter(models.IngredientData.name.ilike(f"%{name}%"))
    if flag:
        query = query.filter(models.IngredientData.flags.ilike(f"%{flag}%"))

    results = query.order_by(models.IngredientData.name).limit(20).all()

    return {
        "results": [
            {"name": r.name, "health_score": r.health_score, "flags": r.flags}
            for r in results
        ]
    }
