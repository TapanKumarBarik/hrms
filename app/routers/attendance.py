from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import uuid

from app.db.session import get_db
from app.db import models
from app.core.auth import get_current_user_with_permissions
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse
)

router = APIRouter()

@router.post("/attendance", response_model=AttendanceResponse)
async def mark_attendance(
    attendance: AttendanceCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Mark attendance for the current day"""
    # Check if attendance already exists for the day
    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.user_id == current_user.id,
        models.Attendance.date == date.today()
    ).first()
    
    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance already marked for today"
        )
    
    new_attendance = models.Attendance(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        date=date.today(),
        check_in=datetime.now(),
        status="present"
    )
    
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    
    return new_attendance

@router.get("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance(
    attendance_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Get attendance details by ID"""
    attendance = db.query(models.Attendance).filter(
        models.Attendance.id == attendance_id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Check permissions
    if attendance.user_id != current_user.id and current_user.role.name not in ["Admin", "HR", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this attendance record"
        )
    
    return attendance

@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: str,
    attendance_update: AttendanceUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Update attendance record"""
    if current_user.role.name not in ["Admin", "HR", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update attendance records"
        )
    
    attendance = db.query(models.Attendance).filter(
        models.Attendance.id == attendance_id
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    for field, value in attendance_update.dict(exclude_unset=True).items():
        setattr(attendance, field, value)
    
    db.commit()
    db.refresh(attendance)
    
    return attendance

@router.get("/attendance", response_model=List[AttendanceResponse])
async def list_attendance(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """List attendance records"""
    if current_user.role.name not in ["Admin", "HR", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all attendance records"
        )
    
    attendance = db.query(models.Attendance).all()
    return attendance