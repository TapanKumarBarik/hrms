from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class DepartmentResponse(DepartmentBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmployeeDepartmentUpdate(BaseModel):
    user_id: str