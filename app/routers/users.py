# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserBase, UserSearchParams
)
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.auth import get_current_active_user, get_current_user_with_permissions

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Get user details
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: str = Path(..., description="The ID of the user to retrieve"),
        current_user: models.User = Depends(get_current_user_with_permissions),
        db: Session = Depends(get_db)
):
    # Check permissions - user can view their own details, managers can view their team,
    # HR and Admin can view all
    if (current_user.id != user_id and
            current_user.role.name not in ["HR", "Admin"] and
            not db.query(models.User).filter(
                models.User.manager_id == current_user.id,
                models.User.id == user_id
            ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this resource"
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# Update user details
@router.put("/{user_id}", response_model=dict)
async def update_user(
        user_data: UserUpdate,
        user_id: str = Path(..., description="The ID of the user to update"),
        current_user: models.User = Depends(get_current_user_with_permissions),
        db: Session = Depends(get_db)
):
    # Check permissions
    if current_user.id != user_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update user fields that are provided
    update_data = user_data.dict(exclude_unset=True)
    
    # Handle manager_id specially
    if "manager_id" in update_data:
        if update_data["manager_id"] == "string" or not update_data["manager_id"]:
            update_data["manager_id"] = None
        else:
            # Verify manager exists
            manager = db.query(models.User).filter(models.User.id == update_data["manager_id"]).first()
            if not manager:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid manager_id provided"
                )

    # Update all fields
    for key, value in update_data.items():
        setattr(user, key, value)

    try:
        db.commit()
        return {"message": "User details updated successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating user: {str(e)}"
        )


# Delete user
@router.delete("/{user_id}", response_model=dict)
async def delete_user(
        user_id: str = Path(..., description="The ID of the user to delete"),
        current_user: models.User = Depends(get_current_user_with_permissions),
        db: Session = Depends(get_db)
):
    # Check permissions - only HR and Admin can delete users
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users"
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Soft delete by setting is_active to False instead of actually deleting
    user.is_active = False
    user.status = "inactive"
    db.commit()

    return {"message": "User deleted successfully"}


# Search users
@router.get("/", response_model=List[UserResponse])
async def search_users(
        name: Optional[str] = Query(None, description="Search by user name"),
        department_id: Optional[str] = Query(None, description="Filter by department ID"),
        role_id: Optional[str] = Query(None, description="Filter by role ID"),
        status: Optional[str] = Query(None, description="Filter by user status"),
        current_user: models.User = Depends(get_current_user_with_permissions),
        db: Session = Depends(get_db)
):
    # Build query
    query = db.query(models.User)

    if name:
        query = query.filter(
            (models.User.first_name.contains(name)) |
            (models.User.last_name.contains(name))
        )

    if department_id:
        query = query.filter(models.User.department_id == department_id)

    if role_id:
        query = query.filter(models.User.role_id == role_id)

    if status:
        query = query.filter(models.User.status == status)

    # For managers, only show their team members
    if current_user.role.name == "Manager":
        query = query.filter(models.User.manager_id == current_user.id)

    users = query.all()
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    # Check permissions
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create users"
        )

    # Check if user with this email already exists
    existing_user = db.query(models.User).filter(
        models.User.email.ilike(user_data.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user_data.email} already exists"
        )

    # Convert user_data to dict and handle manager_id
    user_dict = user_data.dict(exclude={"password"})
    if user_dict.get("manager_id") == "string":
        user_dict.pop("manager_id")
    elif user_dict.get("manager_id"):
        manager = db.query(models.User).filter(models.User.id == user_dict["manager_id"]).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid manager_id provided"
            )

    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = models.User(
        id=str(uuid.uuid4()),
        hashed_password=hashed_password,
        **user_dict
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user