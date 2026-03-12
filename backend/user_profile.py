from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import schemas_profile
from database import get_db
from auth import get_current_user

router = APIRouter()

@router.put("/update", response_model=schemas.UserResponse)
def update_profile(
    profile_data: schemas_profile.UserProfileUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    if profile_data.cgpa is not None:
        current_user.cgpa = profile_data.cgpa
    if profile_data.interests is not None:
        current_user.interests = profile_data.interests
        
    db.commit()
    db.refresh(current_user)
    return current_user
