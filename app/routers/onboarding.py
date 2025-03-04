from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.onboarding import (
    OnboardingTaskCreate, OffboardingTaskCreate,
    TaskUpdate, TaskResponse,
    EmployeeTaskUpdate, EmployeeTaskResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.get("/employees/{employee_id}/onboarding", response_model=List[EmployeeTaskResponse])
async def get_onboarding_status(
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

    tasks = db.query(models.EmployeeOnboarding).filter(
        models.EmployeeOnboarding.user_id == employee_id
    ).all()
    return tasks

@router.put("/employees/{employee_id}/onboarding/{task_id}", response_model=EmployeeTaskResponse)
async def update_onboarding_status(
    employee_id: str,
    task_id: str,
    task_update: EmployeeTaskUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    task = db.query(models.EmployeeOnboarding).filter(
        models.EmployeeOnboarding.user_id == employee_id,
        models.EmployeeOnboarding.id == task_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task_update.status == "completed":
        task.completed_at = datetime.utcnow()

    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

@router.get("/employees/{employee_id}/offboarding", response_model=List[EmployeeTaskResponse])
async def get_offboarding_status(
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

    tasks = db.query(models.EmployeeOffboarding).filter(
        models.EmployeeOffboarding.user_id == employee_id
    ).all()
    return tasks

@router.put("/employees/{employee_id}/offboarding/{task_id}", response_model=EmployeeTaskResponse)
async def update_offboarding_status(
    employee_id: str,
    task_id: str,
    task_update: EmployeeTaskUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    task = db.query(models.EmployeeOffboarding).filter(
        models.EmployeeOffboarding.user_id == employee_id,
        models.EmployeeOffboarding.id == task_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task_update.status == "completed":
        task.completed_at = datetime.utcnow()

    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

@router.get("/onboarding/tasks", response_model=List[TaskResponse])
async def list_onboarding_tasks(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    tasks = db.query(models.OnboardingTask).filter(
        models.OnboardingTask.is_active == True
    ).all()
    return tasks

@router.post("/onboarding/tasks", response_model=TaskResponse)
async def create_onboarding_task(
    task_data: OnboardingTaskCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    task = models.OnboardingTask(
        id=str(uuid.uuid4()),
        **task_data.dict()
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/offboarding/tasks", response_model=List[TaskResponse])
async def list_offboarding_tasks(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    tasks = db.query(models.OffboardingTask).filter(
        models.OffboardingTask.is_active == True
    ).all()
    return tasks

@router.post("/offboarding/tasks", response_model=TaskResponse)
async def create_offboarding_task(
    task_data: OffboardingTaskCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    task = models.OffboardingTask(
        id=str(uuid.uuid4()),
        **task_data.dict()
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task