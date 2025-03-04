from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    department_id: Optional[str] = None
    priority: str = "medium"

class OnboardingTaskCreate(TaskBase):
    role_id: Optional[str] = None

class OffboardingTaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None

class TaskResponse(TaskBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmployeeTaskBase(BaseModel):
    task_id: str
    status: str = "pending"
    notes: Optional[str] = None

class EmployeeTaskUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class EmployeeTaskResponse(BaseModel):
    id: str
    user_id: str
    status: str
    completed_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    task: TaskResponse

    class Config:
        orm_mode = True