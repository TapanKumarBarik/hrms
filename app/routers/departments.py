from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    EmployeeDepartmentUpdate
)
from app.schemas.user import UserResponse
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    department = models.Department(
        id=str(uuid.uuid4()),
        **department_data.dict()
    )
    
    db.add(department)
    db.commit()
    db.refresh(department)
    return department

@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    department = db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    return department

@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    department = db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    for key, value in department_data.dict(exclude_unset=True).items():
        setattr(department, key, value)

    db.commit()
    db.refresh(department)
    return department

@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    department = db.query(models.Department).filter(
        models.Department.id == department_id
    ).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    db.delete(department)
    db.commit()
    return {"message": "Department deleted successfully"}

@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    departments = db.query(models.Department).all()
    return departments

@router.get("/departments/{department_id}/employees", response_model=List[UserResponse])
async def list_department_employees(
    department_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    employees = db.query(models.User).filter(
        models.User.department_id == department_id
    ).all()
    
    return employees

@router.post("/departments/{department_id}/employees")
async def add_employee_to_department(
    department_id: str,
    employee_data: EmployeeDepartmentUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    employee = db.query(models.User).filter(
        models.User.id == employee_data.user_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    employee.department_id = department_id
    db.commit()
    return {"message": "Employee added to department successfully"}

@router.delete("/departments/{department_id}/employees/{employee_id}")
async def remove_employee_from_department(
    department_id: str,
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    employee = db.query(models.User).filter(
        models.User.id == employee_id,
        models.User.department_id == department_id
    ).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found in department"
        )

    employee.department_id = None
    db.commit()
    return {"message": "Employee removed from department successfully"}