from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class PolicyBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    version: str
    effective_date: date
    is_mandatory: bool = True
    status: str = "draft"

class PolicyCreate(PolicyBase):
    pass

class PolicyUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[date] = None
    is_mandatory: Optional[bool] = None
    status: Optional[str] = None

class PolicyResponse(PolicyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ComplianceStatus(BaseModel):
    total_policies: int
    acknowledged_policies: int
    pending_policies: int
    compliance_rate: float
    pending_acknowledgments: List[PolicyResponse]

class PolicyAcknowledgmentCreate(BaseModel):
    policy_id: str

class PolicyAcknowledgmentResponse(BaseModel):
    id: str
    user_id: str
    policy_id: str
    acknowledged_at: datetime
    version_acknowledged: str
    created_at: datetime

    class Config:
        orm_mode = True