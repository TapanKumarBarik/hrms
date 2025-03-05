from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class AttendanceBase(BaseModel):
    date: date
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str
    work_hours: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    check_out: Optional[datetime] = None
    status: Optional[str] = None
    work_hours: Optional[str] = None

class AttendanceResponse(AttendanceBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True