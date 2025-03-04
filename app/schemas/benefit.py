from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class BenefitBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    amount: Optional[float] = None
    is_active: bool = True

class BenefitCreate(BenefitBase):
    pass

class BenefitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    amount: Optional[float] = None
    is_active: Optional[bool] = None

class BenefitResponse(BenefitBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmployeeBenefitBase(BaseModel):
    benefit_id: str
    start_date: date
    end_date: Optional[date] = None
    status: str = "active"

class EmployeeBenefitCreate(EmployeeBenefitBase):
    pass

class EmployeeBenefitUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None

class EmployeeBenefitResponse(EmployeeBenefitBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    benefit: BenefitResponse

    class Config:
        orm_mode = True