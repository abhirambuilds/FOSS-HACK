from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Depends, File, UploadFile, Form, Request, BackgroundTasks
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from ocr_engine import extract_text_from_image
from nlp_parser import clean_ingredient_text, parse_nutrition_facts
import user_routes
import history_routes
import analytics_routes
import suggestion_routes
import notification_routes
import admin_routes
import health_routes
import leaderboard_routes
import badges_routes

# Create tables if they don't exist yet
models.Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="NutriScan API", description="Backend for the NutriScan App")

# Apply Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router, prefix="/api")
app.include_router(history_routes.router, prefix="/api")
app.include_router(analytics_routes.router, prefix="/api")
app.include_router(suggestion_routes.router, prefix="/api")
app.include_router(notification_routes.router, prefix="/api")
app.include_router(admin_routes.router)
app.include_router(health_routes.router, prefix="/api")
app.include_router(leaderboard_routes.router, prefix="/api")
app.include_router(badges_routes.router, prefix="/api")


@app.get("/")
@limiter.limit("20/minute")
def read_root(request: Request):
    return {"status": "NutriScan API is running"}


def _save_scan_to_db(
    db: Session,
    user_id: int,
    product_name: Optional[str],
    health_score: float,
    verdict: str,
    nutrition: dict,
    scanned_ing_models: list,
):
    """Background task: saves scan result to DB and creates a notification if unhealthy."""
    scan_entry = models.ScanHistory(
        user_id=user_id,
        product_name=product_name,
        health_score=health_score,
        verdict=verdict,
        calories=nutrition.get("calories"),
        fat_g=nutrition.get("fat_g"),
        sat_fat_g=nutrition.get("sat_fat_g"),
        trans_fat_g=nutrition.get("trans_fat_g"),
        sodium_mg=nutrition.get("sodium_mg"),
        carbs_g=nutrition.get("carbs_g"),
        fiber_g=nutrition.get("fiber_g"),
        sugar_g=nutrition.get("sugar_g"),
        protein_g=nutrition.get("protein_g"),
        ingredients=scanned_ing_models,
    )
    db.add(scan_entry)
    
    # Update user streak
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        if user.last_scan_date == yesterday:
            user.current_streak += 1
            user.last_scan_date = today
        elif user.last_scan_date == today:
            # Already scanned today, do nothing to streak
            pass
        else:
            # Date is older than yesterday or first scan ever
            user.current_streak = 1
            user.last_scan_date = today
            
    db.commit()

    if verdict == "Unhealthy":
        notif_message = f"You scanned an unhealthy product: {product_name or 'Unknown'}"
        notification = models.Notification(user_id=user_id, message=notif_message)
        db.add(notification)
        db.commit()


@app.post("/api/scan")
@limiter.limit("10/minute")
async def scan_product(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    product_name: Optional[str] = Form(None),
    alert_keyword: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    # Step 1: Extract raw text from the uploaded image via OCR
    image_bytes = await file.read()
    raw_text = extract_text_from_image(image_bytes)

    # Step 2: Parse ingredients and nutrition facts from the OCR text
    ingredients = clean_ingredient_text(raw_text)
    nutrition = parse_nutrition_facts(raw_text)

    from cache import get_cached_ingredient_data

    # Step 3: Look up each ingredient in the DB/Cache to get health scores / flags
    allergy_alerts = []
    total_score = 0.0
    matched_count = 0
    scanned_ing_models = []

    for ingredient in ingredients:
        cached_data = get_cached_ingredient_data(db, ingredient)
        
        if cached_data:
            total_score += cached_data["health_score"]
            matched_count += 1
            if cached_data["flags"]:
                allergy_alerts.append(f"{cached_data['name']}: {cached_data['flags']}")
            
            # Advanced OCR Filter: Check for custom alert keyword
            if alert_keyword:
                keyword_lower = alert_keyword.lower()
                if keyword_lower in ingredient.lower() or keyword_lower in cached_data["name"].lower() or (cached_data["flags"] and keyword_lower in cached_data["flags"].lower()):
                    allergy_alerts.append("CRITICAL ALERT")
            
            ing_model = db.query(models.IngredientData).filter(models.IngredientData.name == cached_data["name"]).first()
            if ing_model:
                scanned_ing_models.append(ing_model)

    health_score = round(total_score / matched_count, 2) if matched_count > 0 else 0.0

    if health_score >= 0.5:
        verdict = "Healthy"
    elif health_score >= 0.0:
        verdict = "Moderate"
    else:
        verdict = "Unhealthy"

    # Offload DB write to background so the API responds immediately
    if user_id is not None:
        background_tasks.add_task(
            _save_scan_to_db,
            db, user_id, product_name, health_score, verdict, nutrition, scanned_ing_models
        )

    suggested_alternatives = []
    if verdict == "Unhealthy":
        from suggestion_routes import get_healthy_alternatives
        bad = ingredients[0] if ingredients else None
        suggested_alternatives = get_healthy_alternatives(db, bad_ingredient=bad)

    return {
        "ingredients_detected": ingredients,
        "allergy_alerts": allergy_alerts,
        "health_score": health_score,
        "verdict": verdict,
        "nutrition_facts": nutrition,
        "suggested_alternatives": suggested_alternatives,
    }


@app.get("/api/scan/barcode/{barcode}")
@limiter.limit("15/minute")
def scan_barcode(
    request: Request,
    barcode: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from external_api import fetch_product_by_barcode
    from cache import get_cached_ingredient_data
    from nlp_parser import clean_ingredient_text
    
    product_data = fetch_product_by_barcode(barcode)
    if not product_data:
        return {"error": "Product not found"}
        
    ingredients_text = product_data.get("ingredients_text", "")
    
    # Process ingredients using existing NLP parser
    # We prefix with 'Ingredients: ' so the parser's regex match works
    ingredients = clean_ingredient_text(f"Ingredients: {ingredients_text}")
    
    allergy_alerts = []
    total_score = 0.0
    matched_count = 0
    scanned_ing_models = []

    for ingredient in ingredients:
        cached_data = get_cached_ingredient_data(db, ingredient)
        
        if cached_data:
            total_score += cached_data["health_score"]
            matched_count += 1
            if cached_data["flags"]:
                allergy_alerts.append(f"{cached_data['name']}: {cached_data['flags']}")
            
            ing_model = db.query(models.IngredientData).filter(models.IngredientData.name == cached_data["name"]).first()
            if ing_model:
                scanned_ing_models.append(ing_model)

    health_score = round(total_score / matched_count, 2) if matched_count > 0 else 0.0

    if health_score >= 0.5:
        verdict = "Healthy"
    elif health_score >= 0.0:
        verdict = "Moderate"
    else:
        verdict = "Unhealthy"

    if user_id is not None:
        scan_entry = models.ScanHistory(
            user_id=user_id,
            product_name=product_data.get("product_name"),
            health_score=health_score,
            verdict=verdict,
            ingredients=scanned_ing_models
        )
        db.add(scan_entry)
        db.commit()

    return {
        "product_info": product_data,
        "ingredients_detected": ingredients,
        "allergy_alerts": allergy_alerts,
        "health_score": health_score,
        "verdict": verdict,
    }