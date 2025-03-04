from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class CertificationTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    issuing_organization: Optional[str] = None
    validity_period: Optional[int] = None

class CertificationTypeCreate(CertificationTypeBase):
    pass

class CertificationTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    issuing_organization: Optional[str] = None
    validity_period: Optional[int] = None

class CertificationTypeResponse(CertificationTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmployeeCertificationBase(BaseModel):
    certification_type_id: str
    certification_number: Optional[str] = None
    issue_date: date
    expiry_date: Optional[date] = None
    status: str = "active"

class EmployeeCertificationCreate(EmployeeCertificationBase):
    pass

class EmployeeCertificationUpdate(BaseModel):
    certification_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[str] = None

class EmployeeCertificationResponse(EmployeeCertificationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    certification_type: CertificationTypeResponse

    class Config:
        orm_mode = True