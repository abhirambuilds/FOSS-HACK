from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    dietary_preference = Column(String, nullable=True)

class IngredientData(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    health_score = Column(Float, default=0.0)      # positive = healthy, negative = unhealthy
    flags = Column(String, nullable=True)           # e.g., "vegan,keto-friendly,allergen"

class ScanHistory(Base):
    __tablename__ = "scan_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String, nullable=True)
    health_score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
