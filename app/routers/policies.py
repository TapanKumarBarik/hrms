from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.db.session import get_db
from app.db import models
from app.schemas.policy import (
    PolicyCreate, PolicyUpdate, PolicyResponse,
    ComplianceStatus, PolicyAcknowledgmentResponse
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.get("/policies", response_model=List[PolicyResponse])
async def get_company_policies(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    policies = db.query(models.Policy).filter(
        models.Policy.status == "active"
    ).all()
    return policies

@router.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    policy_data: PolicyUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    for key, value in policy_data.dict(exclude_unset=True).items():
        setattr(policy, key, value)
    
    db.commit()
    db.refresh(policy)
    return policy

@router.post("/policies", response_model=PolicyResponse)
async def create_policy(
    policy_data: PolicyCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    policy = models.Policy(
        id=str(uuid.uuid4()),
        **policy_data.dict()
    )
    
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy

@router.delete("/policies/{policy_id}")
async def delete_policy(
    policy_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    policy = db.query(models.Policy).filter(models.Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )

    # Soft delete by changing status to archived
    policy.status = "archived"
    db.commit()
    return {"message": "Policy archived successfully"}

@router.get("/policies/compliance", response_model=List[ComplianceStatus])
async def check_compliance_status(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get all active policies
    total_policies = db.query(models.Policy).filter(
        models.Policy.status == "active",
        models.Policy.is_mandatory == True
    ).count()

    # Get compliance status for each user
    users = db.query(models.User).filter(models.User.is_active == True)
    if current_user.role.name == "Manager":
        users = users.filter(models.User.manager_id == current_user.id)

    compliance_stats = []
    for user in users.all():
        acknowledged = db.query(models.PolicyAcknowledgment).filter(
            models.PolicyAcknowledgment.user_id == user.id
        ).count()

        pending_policies = db.query(models.Policy).filter(
            models.Policy.status == "active",
            models.Policy.is_mandatory == True,
            ~models.Policy.id.in_(
                db.query(models.PolicyAcknowledgment.policy_id).filter(
                    models.PolicyAcknowledgment.user_id == user.id
                )
            )
        ).all()

        compliance_stats.append(ComplianceStatus(
            total_policies=total_policies,
            acknowledged_policies=acknowledged,
            pending_policies=len(pending_policies),
            compliance_rate=acknowledged/total_policies if total_policies > 0 else 1.0,
            pending_acknowledgments=pending_policies
        ))

    return compliance_stats

@router.get("/employees/{employee_id}/compliance", response_model=ComplianceStatus)
async def get_employee_compliance_status(
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

    total_policies = db.query(models.Policy).filter(
        models.Policy.status == "active",
        models.Policy.is_mandatory == True
    ).count()

    acknowledged = db.query(models.PolicyAcknowledgment).filter(
        models.PolicyAcknowledgment.user_id == employee_id
    ).count()

    pending_policies = db.query(models.Policy).filter(
        models.Policy.status == "active",
        models.Policy.is_mandatory == True,
        ~models.Policy.id.in_(
            db.query(models.PolicyAcknowledgment.policy_id).filter(
                models.PolicyAcknowledgment.user_id == employee_id
            )
        )
    ).all()

    return ComplianceStatus(
        total_policies=total_policies,
        acknowledged_policies=acknowledged,
        pending_policies=len(pending_policies),
        compliance_rate=acknowledged/total_policies if total_policies > 0 else 1.0,
        pending_acknowledgments=pending_policies
    )