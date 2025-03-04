# app/routers/leaves.py

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import date, datetime

from app.db.session import get_db
from app.db import models
from app.schemas.leave import (
    LeaveCreate, LeaveUpdate, LeaveResponse,
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse,
    LeaveBalanceCreate, LeaveBalanceUpdate, LeaveBalanceResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

# Get Employee Leave
@router.get("/employees/{employee_id}/leaves", response_model=List[LeaveResponse])
async def get_employee_leaves(
    employee_id: str = Path(..., description="The ID of the employee"),
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if (current_user.id != employee_id and 
        current_user.role.name not in ["Manager", "HR", "Admin"] and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == employee_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leaves = db.query(models.Leave).filter(models.Leave.user_id == employee_id).all()
    return leaves

# Apply Leave
@router.post("/employees/{employee_id}/leaves", response_model=LeaveResponse)
async def apply_leave(
    leave_data: LeaveCreate,
    employee_id: str = Path(..., description="The ID of the employee"),
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    # Only allow self-application or HR/Admin
    if current_user.id != employee_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Validate leave type
    leave_type = db.query(models.LeaveType).filter(
        models.LeaveType.id == leave_data.leave_type_id,
        models.LeaveType.is_active == True
    ).first()
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave type"
        )

    # Check leave balance
    balance = db.query(models.LeaveBalance).filter(
        models.LeaveBalance.user_id == employee_id,
        models.LeaveBalance.leave_type_id == leave_data.leave_type_id,
        models.LeaveBalance.year == datetime.now().year
    ).first()

    if not balance or (balance.total_days - balance.used_days) <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient leave balance"
        )

    # Create leave request
    leave = models.Leave(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        status="pending",
        **leave_data.dict()
    )
    
    db.add(leave)
    db.commit()
    db.refresh(leave)
    
    return leave

# Approve Leave
@router.put("/leaves/{leave_id}/approve", response_model=LeaveResponse)
async def approve_leave(
    leave_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )

    # Manager can only approve their team's leaves
    if (current_user.role.name == "Manager" and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == leave.user_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only approve team member leaves"
        )

    leave.status = "approved"
    db.commit()
    db.refresh(leave)
    
    return leave

# Reject Leave
@router.put("/leaves/{leave_id}/reject", response_model=LeaveResponse)
async def reject_leave(
    leave_id: str,
    comment: str = Query(..., description="Reason for rejection"),
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )

    # Manager can only reject their team's leaves
    if (current_user.role.name == "Manager" and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == leave.user_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only reject team member leaves"
        )

    leave.status = "rejected"
    leave.comment = comment
    db.commit()
    db.refresh(leave)
    
    return leave

# Cancel Leave
@router.delete("/leaves/{leave_id}", response_model=dict)
async def cancel_leave(
    leave_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    leave = db.query(models.Leave).filter(models.Leave.id == leave_id).first()
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave not found"
        )

    # Only self, manager, HR or admin can cancel
    if (current_user.id != leave.user_id and
        current_user.role.name not in ["HR", "Admin"] and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == leave.user_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    db.delete(leave)
    db.commit()
    
    return {"message": "Leave cancelled successfully"}

# List All Leaves
@router.get("/leaves", response_model=List[LeaveResponse])
async def list_leaves(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[date] = Query(None, description="Filter from date"),
    to_date: Optional[date] = Query(None, description="Filter to date")
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    query = db.query(models.Leave)

    # Managers can only see their team's leaves
    if current_user.role.name == "Manager":
        query = query.join(models.User).filter(models.User.manager_id == current_user.id)

    if status:
        query = query.filter(models.Leave.status == status)
    if from_date:
        query = query.filter(models.Leave.start_date >= from_date)
    if to_date:
        query = query.filter(models.Leave.end_date <= to_date)

    return query.all()

# Get Leave Balance
@router.get("/employees/{employee_id}/leave-balance", response_model=List[LeaveBalanceResponse])
async def get_leave_balance(
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if (current_user.id != employee_id and 
        current_user.role.name not in ["Manager", "HR", "Admin"] and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == employee_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    balances = db.query(models.LeaveBalance).filter(
        models.LeaveBalance.user_id == employee_id,
        models.LeaveBalance.year == datetime.now().year
    ).all()
    return balances

# Update Leave Balance
@router.put("/employees/{employee_id}/leave-balance", response_model=LeaveBalanceResponse)
async def update_leave_balance(
    employee_id: str,
    balance_data: LeaveBalanceUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    balance = db.query(models.LeaveBalance).filter(
        models.LeaveBalance.user_id == employee_id,
        models.LeaveBalance.leave_type_id == balance_data.leave_type_id,
        models.LeaveBalance.year == datetime.now().year
    ).first()

    if not balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave balance not found"
        )

    for key, value in balance_data.dict().items():
        setattr(balance, key, value)

    db.commit()
    db.refresh(balance)
    
    return balance

# Get Leave Types
@router.get("/leave-types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leave_types = db.query(models.LeaveType).filter(models.LeaveType.is_active == True).all()
    return leave_types

# Create Leave Type
@router.post("/leave-types", response_model=LeaveTypeResponse)
async def create_leave_type(
    leave_type_data: LeaveTypeCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leave_type = models.LeaveType(
        id=str(uuid.uuid4()),
        **leave_type_data.dict()
    )
    
    db.add(leave_type)
    db.commit()
    db.refresh(leave_type)
    
    return leave_type

# Update Leave Type
@router.put("/leave-types/{leave_type_id}", response_model=LeaveTypeResponse)
async def update_leave_type(
    leave_type_id: str,
    leave_type_data: LeaveTypeUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leave_type = db.query(models.LeaveType).filter(models.LeaveType.id == leave_type_id).first()
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    for key, value in leave_type_data.dict().items():
        setattr(leave_type, key, value)

    db.commit()
    db.refresh(leave_type)
    
    return leave_type

# Delete Leave Type
@router.delete("/leave-types/{leave_type_id}", response_model=dict)
async def delete_leave_type(
    leave_type_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    leave_type = db.query(models.LeaveType).filter(models.LeaveType.id == leave_type_id).first()
    if not leave_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    db.delete(leave_type)
    db.commit()
    
    return {"message": "Leave type deleted successfully"}