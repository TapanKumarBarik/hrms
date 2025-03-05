from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectAssignmentCreate, ProjectAssignmentUpdate, ProjectAssignmentResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.get("/users/{user_id}/projects", response_model=List[ProjectAssignmentResponse])
async def list_user_projects(
    user_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """List all projects assigned to a user"""
    if (current_user.id != user_id and 
        current_user.role.name not in ["Manager", "HR", "Admin"] and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == user_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    assignments = db.query(models.ProjectAssignment).filter(
        models.ProjectAssignment.user_id == user_id,
        models.ProjectAssignment.status == "active"
    ).all()
    return assignments

@router.post("/users/{user_id}/projects", response_model=ProjectAssignmentResponse)
async def assign_project(
    user_id: str,
    assignment_data: ProjectAssignmentCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Assign a project to a user"""
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Verify project exists
    project = db.query(models.Project).filter(
        models.Project.id == assignment_data.project_id,
        models.Project.status == "active"
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or inactive"
        )

    # Check if user is already assigned to this project
    existing_assignment = db.query(models.ProjectAssignment).filter(
        models.ProjectAssignment.user_id == user_id,
        models.ProjectAssignment.project_id == assignment_data.project_id,
        models.ProjectAssignment.status == "active"
    ).first()
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already assigned to this project"
        )

    assignment = models.ProjectAssignment(
        id=str(uuid.uuid4()),
        user_id=user_id,
        assigned_by=current_user.id,
        **assignment_data.dict()
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

@router.delete("/users/{user_id}/projects/{project_id}")
async def remove_project(
    user_id: str,
    project_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    """Remove a project assignment from a user"""
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    assignment = db.query(models.ProjectAssignment).filter(
        models.ProjectAssignment.user_id == user_id,
        models.ProjectAssignment.project_id == project_id,
        models.ProjectAssignment.status == "active"
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project assignment not found"
        )

    assignment.status = "removed"
    assignment.end_date = datetime.now().date()
    db.commit()
    return {"message": "Project assignment removed successfully"}