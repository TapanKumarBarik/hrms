from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.certification import (
    CertificationTypeCreate, CertificationTypeUpdate, CertificationTypeResponse,
    EmployeeCertificationCreate, EmployeeCertificationUpdate, EmployeeCertificationResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.get("/employees/{employee_id}/certifications", response_model=List[EmployeeCertificationResponse])
async def get_employee_certifications(
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

    certifications = db.query(models.EmployeeCertification).filter(
        models.EmployeeCertification.user_id == employee_id
    ).all()
    return certifications

@router.post("/employees/{employee_id}/certifications", response_model=EmployeeCertificationResponse)
async def add_certification(
    employee_id: str,
    certification_data: EmployeeCertificationCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.id != employee_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    certification = models.EmployeeCertification(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        **certification_data.dict()
    )
    
    db.add(certification)
    db.commit()
    db.refresh(certification)
    return certification

@router.put("/employees/{employee_id}/certifications/{certification_id}", 
           response_model=EmployeeCertificationResponse)
async def update_certification(
    employee_id: str,
    certification_id: str,
    certification_data: EmployeeCertificationUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.id != employee_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    certification = db.query(models.EmployeeCertification).filter(
        models.EmployeeCertification.id == certification_id,
        models.EmployeeCertification.user_id == employee_id
    ).first()

    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found"
        )

    for key, value in certification_data.dict(exclude_unset=True).items():
        setattr(certification, key, value)
    
    db.commit()
    db.refresh(certification)
    return certification

@router.delete("/employees/{employee_id}/certifications/{certification_id}")
async def remove_certification(
    employee_id: str,
    certification_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.id != employee_id and current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    certification = db.query(models.EmployeeCertification).filter(
        models.EmployeeCertification.id == certification_id,
        models.EmployeeCertification.user_id == employee_id
    ).first()

    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found"
        )

    db.delete(certification)
    db.commit()
    return {"message": "Certification removed successfully"}

@router.get("/certifications", response_model=List[CertificationTypeResponse])
async def list_certifications(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    certifications = db.query(models.CertificationType).all()
    return certifications

@router.post("/certifications", response_model=CertificationTypeResponse)
async def create_certification_type(
    certification_data: CertificationTypeCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    certification_type = models.CertificationType(
        id=str(uuid.uuid4()),
        **certification_data.dict()
    )
    
    db.add(certification_type)
    db.commit()
    db.refresh(certification_type)
    return certification_type

@router.put("/certifications/{certification_id}", response_model=CertificationTypeResponse)
async def update_certification_type(
    certification_id: str,
    certification_data: CertificationTypeUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    certification_type = db.query(models.CertificationType).filter(
        models.CertificationType.id == certification_id
    ).first()

    if not certification_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification type not found"
        )

    for key, value in certification_data.dict(exclude_unset=True).items():
        setattr(certification_type, key, value)
    
    db.commit()
    db.refresh(certification_type)
    return certification_type

@router.delete("/certifications/{certification_id}")
async def delete_certification_type(
    certification_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    certification_type = db.query(models.CertificationType).filter(
        models.CertificationType.id == certification_id
    ).first()

    if not certification_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification type not found"
        )

    db.delete(certification_type)
    db.commit()
    return {"message": "Certification type deleted successfully"}