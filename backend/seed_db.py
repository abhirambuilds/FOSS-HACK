from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

def seed_database():
    # Create tables if not exist
    models.Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    # List of common ingredients with health scores and flags
    initial_ingredients = [
        {"name": "Sugar", "health_score": -0.8, "flags": "high_sugar,diabetic_risk"},
        {"name": "Palm Oil", "health_score": -0.6, "flags": "high_saturated_fat"},
        {"name": "Maltodextrin", "health_score": -0.5, "flags": "high_gi"},
        {"name": "High Fructose Corn Syrup", "health_score": -0.9, "flags": "high_sugar,metabolic_risk"},
        {"name": "Enriched Flour", "health_score": -0.2, "flags": "refined_carb,gluten"},
        {"name": "Whole Wheat Flour", "health_score": 0.5, "flags": "gluten,fiber"},
        {"name": "Yellow 5", "health_score": -0.7, "flags": "artificial_dye"},
        {"name": "Red 40", "health_score": -0.7, "flags": "artificial_dye"},
        {"name": "Sodium Benzoate", "health_score": -0.6, "flags": "preservative"},
        {"name": "Ascorbic Acid", "health_score": 0.8, "flags": "vitamin_c"},
        {"name": "Citric Acid", "health_score": 0.2, "flags": "preservative"},
        {"name": "Salt", "health_score": -0.3, "flags": "high_sodium"},
        {"name": "Oats", "health_score": 0.9, "flags": "fiber,gluten_free_usually"},
        {"name": "Almonds", "health_score": 0.9, "flags": "nut_allergen,healthy_fats"},
        {"name": "Milk", "health_score": 0.4, "flags": "dairy_allergen,lactose"},
        {"name": "Soy Lecithin", "health_score": 0.0, "flags": "soy_allergen"}
    ]
    
    print("Seeding database...")
    added_count = 0
    for item in initial_ingredients:
        # Check if already exists
        existing = db.query(models.IngredientData).filter(models.IngredientData.name.ilike(item["name"])).first()
        if not existing:
            new_ingredient = models.IngredientData(
                name=item["name"],
                health_score=item["health_score"],
                flags=item["flags"]
            )
            db.add(new_ingredient)
            added_count += 1
            
    db.commit()
    db.close()
    print(f"Database seeded successfully. Added {added_count} new ingredients.")

if __name__ == "__main__":
    seed_database()
