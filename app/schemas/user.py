from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = "active"

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    joining_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserSearchParams(BaseModel):
    name: Optional[str] = None
    department_id: Optional[str] = None
    role_id: Optional[str] = None
    status: Optional[str] = None