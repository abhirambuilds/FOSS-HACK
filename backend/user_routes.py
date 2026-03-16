from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import timedelta, datetime, time

import models
from database import get_db
from auth import get_password_hash, verify_password, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    password: str
    dietary_preference: Optional[str] = None

class UserPreferencesUpdate(BaseModel):
    dietary_preference: str

class UserGoalsUpdate(BaseModel):
    target_calories: Optional[float] = None
    target_protein: Optional[float] = None
    target_fat: Optional[float] = None
    target_carbs: Optional[float] = None

class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserGoalsResponse(BaseModel):
    target_calories: Optional[float] = None
    target_protein: Optional[float] = None
    target_fat: Optional[float] = None
    target_carbs: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    dietary_preference: Optional[str] = None
    current_streak: int

    model_config = ConfigDict(from_attributes=True)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        hashed_password=hashed_pwd,
        dietary_preference=user.dietary_preference
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}/preferences", response_model=UserResponse)
def update_user_preferences(
    user_id: int, 
    prefs: UserPreferencesUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.dietary_preference = prefs.dietary_preference
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/users/{user_id}/goals", response_model=UserGoalsResponse)
def update_user_goals(
    user_id: int, 
    goals: UserGoalsUpdate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if goals.target_calories is not None:
        db_user.target_calories = goals.target_calories
    if goals.target_protein is not None:
        db_user.target_protein = goals.target_protein
    if goals.target_fat is not None:
        db_user.target_fat = goals.target_fat
    if goals.target_carbs is not None:
        db_user.target_carbs = goals.target_carbs

    db.commit()
    db.refresh(db_user)
    return db_user

@router.put("/users/{user_id}/profile", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    profile: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.display_name = profile.display_name
    db_user.avatar_url = profile.avatar_url

    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}/progress")
def get_user_progress(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    today = datetime.utcnow().date()
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)
    
    records = db.query(models.ScanHistory).filter(
        models.ScanHistory.user_id == user_id,
        models.ScanHistory.created_at >= today_start,
        models.ScanHistory.created_at <= today_end
    ).all()
    
    total_calories = sum(r.calories for r in records if r.calories)
    total_protein = sum(r.protein_g for r in records if r.protein_g)
    total_fat = sum(r.fat_g for r in records if r.fat_g)
    total_carbs = sum(r.carbs_g for r in records if r.carbs_g)
    
    def calc_percentage(current, target):
        if not target or target <= 0:
            return 0.0
        return round((current / target) * 100, 2)
        
    return {
        "calories": {
            "current": round(total_calories, 2),
            "target": db_user.target_calories,
            "percentage_completed": calc_percentage(total_calories, db_user.target_calories)
        },
        "protein": {
            "current": round(total_protein, 2),
            "target": db_user.target_protein,
            "percentage_completed": calc_percentage(total_protein, db_user.target_protein)
        },
        "fat": {
            "current": round(total_fat, 2),
            "target": db_user.target_fat,
            "percentage_completed": calc_percentage(total_fat, db_user.target_fat)
        },
        "carbs": {
            "current": round(total_carbs, 2),
            "target": db_user.target_carbs,
            "percentage_completed": calc_percentage(total_carbs, db_user.target_carbs)
        }
    }
#-----
#-----