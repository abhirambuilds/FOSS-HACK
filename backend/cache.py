from expiringdict import ExpiringDict
from typing import Optional
from sqlalchemy.orm import Session
import models

# In-memory cache: max 1000 items, expires in 24 hours (86400 seconds)
# We cache the health_score and flags for a given ingredient name
ingredient_cache = ExpiringDict(max_len=1000, max_age_seconds=86400)


def get_cached_ingredient_data(db: Session, ingredient_name: str) -> Optional[dict]:
    """
    Looks up ingredient in cache first. If not found, fetches from DB and caches it.
    """
    # Normalize name for cache key
    cache_key = ingredient_name.strip().lower()

    # 1. Check Cache
    cached_data = ingredient_cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    # 2. Check Database
    row = (
        db.query(models.IngredientData)
        .filter(models.IngredientData.name.ilike(f"%{ingredient_name}%"))
        .first()
    )

    if row:
        # 3. Store in Cache
        data = {
            "name": row.name,
            "health_score": row.health_score,
            "flags": row.flags,
        }
        ingredient_cache[cache_key] = data
        return data

    return None
