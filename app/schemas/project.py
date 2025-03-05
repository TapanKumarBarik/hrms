from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "active"
    priority: str = "medium"
    budget: Optional[float] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    budget: Optional[float] = None

class ProjectResponse(ProjectBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProjectAssignmentBase(BaseModel):
    project_id: str
    role: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    allocation_percentage: Optional[int] = 100

class ProjectAssignmentCreate(ProjectAssignmentBase):
    pass

class ProjectAssignmentUpdate(BaseModel):
    role: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    allocation_percentage: Optional[int] = None
    status: Optional[str] = None

class ProjectAssignmentResponse(ProjectAssignmentBase):
    id: str
    user_id: str
    assigned_by: str
    status: str
    created_at: datetime
    updated_at: datetime
    project: ProjectResponse

    class Config:
        orm_mode = True