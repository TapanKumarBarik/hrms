from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.benefit import (
    BenefitCreate, BenefitUpdate, BenefitResponse,
    EmployeeBenefitCreate, EmployeeBenefitUpdate, EmployeeBenefitResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.get("/benefits", response_model=List[BenefitResponse])
async def list_benefits(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    benefits = db.query(models.Benefit).filter(
        models.Benefit.is_active == True
    ).all()
    return benefits

@router.post("/employees/{employee_id}/benefits", response_model=EmployeeBenefitResponse)
async def assign_benefit(
    employee_id: str,
    benefit_data: EmployeeBenefitCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    employee_benefit = models.EmployeeBenefit(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        **benefit_data.dict()
    )
    
    db.add(employee_benefit)
    db.commit()
    db.refresh(employee_benefit)
    return employee_benefit

@router.put("/employees/{employee_id}/benefits/{benefit_id}", 
           response_model=EmployeeBenefitResponse)
async def update_employee_benefit(
    employee_id: str,
    benefit_id: str,
    benefit_data: EmployeeBenefitUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    benefit = db.query(models.EmployeeBenefit).filter(
        models.EmployeeBenefit.id == benefit_id,
        models.EmployeeBenefit.user_id == employee_id
    ).first()
    
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benefit not found"
        )

    for key, value in benefit_data.dict(exclude_unset=True).items():
        setattr(benefit, key, value)

    db.commit()
    db.refresh(benefit)
    return benefit

@router.delete("/employees/{employee_id}/benefits/{benefit_id}")
async def remove_employee_benefit(
    employee_id: str,
    benefit_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    benefit = db.query(models.EmployeeBenefit).filter(
        models.EmployeeBenefit.id == benefit_id,
        models.EmployeeBenefit.user_id == employee_id
    ).first()
    
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benefit not found"
        )

    benefit.status = "inactive"
    db.commit()
    return {"message": "Benefit removed successfully"}

@router.get("/employees/{employee_id}/benefits", response_model=List[EmployeeBenefitResponse])
async def list_employee_benefits(
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

    benefits = db.query(models.EmployeeBenefit).filter(
        models.EmployeeBenefit.user_id == employee_id
    ).all()
    return benefits

@router.post("/benefits", response_model=BenefitResponse)
async def create_benefit(
    benefit_data: BenefitCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    benefit = models.Benefit(
        id=str(uuid.uuid4()),
        **benefit_data.dict()
    )
    
    db.add(benefit)
    db.commit()
    db.refresh(benefit)
    return benefit

@router.put("/benefits/{benefit_id}", response_model=BenefitResponse)
async def update_benefit_details(
    benefit_id: str,
    benefit_data: BenefitUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    benefit = db.query(models.Benefit).filter(
        models.Benefit.id == benefit_id
    ).first()
    
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benefit not found"
        )

    for key, value in benefit_data.dict(exclude_unset=True).items():
        setattr(benefit, key, value)

    db.commit()
    db.refresh(benefit)
    return benefit

@router.delete("/benefits/{benefit_id}")
async def delete_benefit(
    benefit_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    benefit = db.query(models.Benefit).filter(
        models.Benefit.id == benefit_id
    ).first()
    
    if not benefit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benefit not found"
        )

    benefit.is_active = False
    db.commit()
    return {"message": "Benefit deleted successfully"}