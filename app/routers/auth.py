# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.db.session import get_db
from app.db import models
from app.schemas.token import Token
from app.schemas.user import UserCreate
router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    print(form_data)
    # Authenticate user
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    print("-----------------")
    print(user)
    print("-----------------")
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/create-superuser", status_code=status.HTTP_201_CREATED)
async def create_superuser(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if any admin user exists
    admin_role = db.query(models.Role).filter_by(name="Admin").first()
    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please run database initialization first"
        )
    
    if db.query(models.User).filter_by(role_id=admin_role.id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superuser already exists"
        )
    
    # Create superuser
    hashed_password = get_password_hash(user_data.password)
    user = models.User(
        id=str(uuid.uuid4()),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=hashed_password,
        role_id=admin_role.id,
        status="active",
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Superuser created successfully"}