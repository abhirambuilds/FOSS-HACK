from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Depends, File, UploadFile, Form, Request
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


@app.get("/")
@limiter.limit("20/minute")
def read_root(request: Request):
    return {"status": "NutriScan API is running"}


@app.post("/api/scan")
@limiter.limit("10/minute")
async def scan_product(
    request: Request,
    file: UploadFile = File(...),
    user_id: Optional[int] = Form(None),
    product_name: Optional[str] = Form(None),
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
            ingredients=scanned_ing_models
        )
        db.add(scan_entry)
        db.commit()

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