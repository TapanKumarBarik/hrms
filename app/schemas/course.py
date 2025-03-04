from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    status: str = "active"

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    category: Optional[str] = None
    status: Optional[str] = None

class CourseResponse(CourseBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EnrollmentBase(BaseModel):
    course_id: str
    status: str = "enrolled"

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    status: str
    completion_date: Optional[datetime] = None

class EnrollmentResponse(EnrollmentBase):
    id: str
    user_id: str
    assigned_by: Optional[str]
    completion_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    course: CourseResponse

    class Config:
        orm_mode = True