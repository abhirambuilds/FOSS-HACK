from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    dietary_preference = Column(String, nullable=True)
    target_calories = Column(Float, nullable=True)
    target_protein = Column(Float, nullable=True)
    target_fat = Column(Float, nullable=True)
    target_carbs = Column(Float, nullable=True)
    current_streak = Column(Integer, default=0)
    last_scan_date = Column(Date, nullable=True)

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

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
