from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class LeaveTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    default_days: int = 0
    is_active: bool = True

class LeaveTypeCreate(LeaveTypeBase):
    pass

class LeaveTypeUpdate(LeaveTypeBase):
    name: Optional[str] = None
    default_days: Optional[int] = None
    is_active: Optional[bool] = None

class LeaveTypeResponse(LeaveTypeBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LeaveBalanceBase(BaseModel):
    leave_type_id: str
    year: int
    total_days: int
    used_days: int = 0

class LeaveBalanceCreate(LeaveBalanceBase):
    user_id: str

class LeaveBalanceUpdate(BaseModel):
    total_days: Optional[int] = None
    used_days: Optional[int] = None

class LeaveBalanceResponse(LeaveBalanceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LeaveBase(BaseModel):
    leave_type_id: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveCreate(LeaveBase):
    pass

class LeaveUpdate(BaseModel):
    status: str
    comment: Optional[str] = None

class LeaveResponse(LeaveBase):
    id: str
    user_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    leave_type: LeaveTypeResponse

    class Config:
        orm_mode = True