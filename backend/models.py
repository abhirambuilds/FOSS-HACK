from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    dietary_preference = Column(String, nullable=True)

class IngredientData(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    health_score = Column(Float, default=0.0)      # positive = healthy, negative = unhealthy
    flags = Column(String, nullable=True)           # e.g., "vegan,keto-friendly,allergen"

scan_ingredients_association = Table(
    "scan_ingredients",
    Base.metadata,
    Column("scan_id", Integer, ForeignKey("scan_history.id"), primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id"), primary_key=True)
)

class ScanHistory(Base):
    __tablename__ = "scan_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String, nullable=True)
    health_score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)

    # Added relationship
    ingredients = relationship("IngredientData", secondary=scan_ingredients_association)

    # Nutrition Facts macros extracted from the label
    calories = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    sat_fat_g = Column(Float, nullable=True)
    trans_fat_g = Column(Float, nullable=True)
    sodium_mg = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    sugar_g = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
