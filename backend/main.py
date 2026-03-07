from fastapi import FastAPI, Depends, File, UploadFile
from sqlalchemy.orm import Session

import models
from database import engine, get_db
from ocr_engine import extract_text_from_image
from nlp_parser import clean_ingredient_text

# Create tables if they don't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriScan API", description="Backend for the NutriScan App")


@app.get("/")
def read_root():
    return {"status": "NutriScan API is running"}


@app.post("/api/scan")
async def scan_product(
    file: UploadFile = File(...),
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

    return {
        "ingredients_detected": ingredients,
        "allergy_alerts": allergy_alerts,
        "health_score": health_score,
        "verdict": verdict,
    }