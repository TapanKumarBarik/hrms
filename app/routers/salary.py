# app/routers/salary.py
from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.salary import (
    SalaryBase, SalaryCreate, SalaryUpdate, SalaryResponse,
    PayslipCreate, PayslipResponse,
    TaxInfoCreate, TaxInfoUpdate, TaxInfoResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

# Check Salary as Employee/Manager
@router.get("/employees/{employee_id}/salary", response_model=SalaryResponse)
async def get_salary(
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    # Check permissions
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

    salary = db.query(models.Salary).filter(
        models.Salary.user_id == employee_id
    ).order_by(models.Salary.effective_date.desc()).first()
    
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary details not found"
        )
    
    return salary

# Update Salary
@router.put("/employees/{employee_id}/salary", response_model=SalaryResponse)
async def update_salary(
    employee_id: str,
    salary_data: SalaryUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Create new salary record
    new_salary = models.Salary(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        **salary_data.dict(exclude_unset=True)
    )
    
    # Calculate gross and net salary
    new_salary.gross_salary = new_salary.basic_salary + new_salary.allowances
    new_salary.net_salary = new_salary.gross_salary - new_salary.deductions
    
    db.add(new_salary)
    db.commit()
    db.refresh(new_salary)
    
    return new_salary

# Get Salary History
@router.get("/employees/{employee_id}/salary-history", response_model=List[SalaryResponse])
async def get_salary_history(
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

    salaries = db.query(models.Salary).filter(
        models.Salary.user_id == employee_id
    ).order_by(models.Salary.effective_date.desc()).all()
    
    return salaries

# Generate Payslip
@router.post("/employees/{employee_id}/payslip", response_model=PayslipResponse)
async def generate_payslip(
    employee_id: str,
    payslip_data: PayslipCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get current salary details
    salary = db.query(models.Salary).filter(
        models.Salary.user_id == employee_id
    ).order_by(models.Salary.effective_date.desc()).first()
    
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary details not found"
        )
    
    # Create payslip
    payslip = models.Payslip(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        basic_salary=salary.basic_salary,
        allowances=salary.allowances,
        deductions=salary.deductions,
        gross_salary=salary.gross_salary,
        net_salary=salary.net_salary,
        status="generated",
        generated_at=datetime.utcnow(),
        **payslip_data.dict()
    )
    
    db.add(payslip)
    db.commit()
    db.refresh(payslip)
    
    return payslip

# List Payslips
@router.get("/employees/{employee_id}/payslips", response_model=List[PayslipResponse])
async def list_payslips(
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.id != employee_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    payslips = db.query(models.Payslip).filter(
        models.Payslip.user_id == employee_id
    ).order_by(models.Payslip.year.desc(), models.Payslip.month.desc()).all()
    
    return payslips

# Get Tax Info
@router.get("/employees/{employee_id}/tax", response_model=TaxInfoResponse)
async def get_tax_info(
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.id != employee_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    tax_info = db.query(models.TaxInfo).filter(models.TaxInfo.user_id == employee_id).first()
    if not tax_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tax information not found"
        )
        
    return tax_info

# Update Tax Info
@router.put("/employees/{employee_id}/tax", response_model=TaxInfoResponse)
async def update_tax_info(
    employee_id: str,
    tax_data: TaxInfoUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    tax_info = db.query(models.TaxInfo).filter(models.TaxInfo.user_id == employee_id).first()
    if not tax_info:
        tax_info = models.TaxInfo(
            id=str(uuid.uuid4()),
            user_id=employee_id
        )
        db.add(tax_info)
        
    for key, value in tax_data.dict(exclude_unset=True).items():
        setattr(tax_info, key, value)
        
    db.commit()
    db.refresh(tax_info)
    
    return tax_info