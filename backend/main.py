from fastapi import FastAPI, Depends, File, UploadFile, Form
from typing import Optional
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from ocr_engine import extract_text_from_image
from nlp_parser import clean_ingredient_text, parse_nutrition_facts
import user_routes
import history_routes

# Create tables if they don't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriScan API", description="Backend for the NutriScan App")

app.include_router(user_routes.router, prefix="/api")
app.include_router(history_routes.router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "NutriScan API is running"}


@app.post("/api/scan")
async def scan_product(
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

    for ingredient in ingredients:
        cached_data = get_cached_ingredient_data(db, ingredient)
        
        if cached_data:
            total_score += cached_data["health_score"]
            matched_count += 1
            if cached_data["flags"]:
                allergy_alerts.append(f"{cached_data['name']}: {cached_data['flags']}")

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
        )
        db.add(scan_entry)
        db.commit()

    return {
        "ingredients_detected": ingredients,
        "allergy_alerts": allergy_alerts,
        "health_score": health_score,
        "verdict": verdict,
        "nutrition_facts": nutrition,
    }