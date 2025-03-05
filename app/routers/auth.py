# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
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
from app.schemas.auth import (
    LoginRequest, RegisterRequest, PasswordResetRequest,
    PasswordResetConfirm, ChangePasswordRequest, AuthResponse
)
from typing import Optional
from app.core.auth import get_current_user_with_permissions


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



@router.post("/login", response_model=AuthResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token"""
    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": user.role.name
    }

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if user exists
    if db.query(models.User).filter(models.User.email == register_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Get default role (Employee)
    default_role = db.query(models.Role).filter(models.Role.name == "Employee").first()
    if not default_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not found"
        )

    # Create user
    hashed_password = get_password_hash(register_data.password)
    user = models.User(
        id=str(uuid.uuid4()),
        email=register_data.email,
        hashed_password=hashed_password,
        first_name=register_data.first_name,
        last_name=register_data.last_name,
        phone_number=register_data.phone_number,
        role_id=default_role.id,
        is_active=True,
        status="active"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token
    access_token = create_access_token(data={"sub": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "role": "Employee"
    }

@router.post("/logout")
async def logout(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Log out user by invalidating JWT token"""
    # Note: JWT tokens are stateless, so we can't really "invalidate" them
    # In a production environment, you might want to implement a token blacklist
    # For now, we'll just return a success message
    return {"message": "Successfully logged out"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Initiate password reset process"""
    user = db.query(models.User).filter(models.User.email == reset_data.email).first()
    if not user:
        # Return success even if user doesn't exist to prevent email enumeration
        return {"message": "If your email is registered, you will receive a password reset link"}

    # Generate password reset token
    reset_token = create_access_token(
        data={"sub": user.id, "type": "password_reset"},
        expires_delta=timedelta(hours=1)
    )

    # In a real application, send email with reset link
    # background_tasks.add_task(send_reset_email, user.email, reset_token)

    return {"message": "If your email is registered, you will receive a password reset link"}

@router.post("/reset-password/confirm")
async def reset_password_confirm(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Complete password reset process"""
    try:
        payload = jwt.decode(reset_data.token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.hashed_password = get_password_hash(reset_data.new_password)
    db.commit()

    return {"message": "Password has been reset successfully"}

@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Change user password"""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}