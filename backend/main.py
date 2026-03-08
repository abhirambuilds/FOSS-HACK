from fastapi import FastAPI, Depends, File, UploadFile, Form
from typing import Optional
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from ocr_engine import extract_text_from_image
from nlp_parser import clean_ingredient_text
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

    # Step 2: Parse ingredients from the OCR text using spaCy
    ingredients = clean_ingredient_text(raw_text)

    # Step 3: Look up each ingredient in the DB to get health scores / flags
    allergy_alerts = []
    total_score = 0.0
    matched_count = 0

    for ingredient in ingredients:
        row = (
            db.query(models.IngredientData)
            .filter(models.IngredientData.name.ilike(f"%{ingredient}%"))
            .first()
        )
        if row:
            total_score += row.health_score
            matched_count += 1
            if row.flags:
                allergy_alerts.append(f"{row.name}: {row.flags}")

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
        )
        db.add(scan_entry)
        db.commit()

    return {
        "ingredients_detected": ingredients,
        "allergy_alerts": allergy_alerts,
        "health_score": health_score,
        "verdict": verdict,
    }