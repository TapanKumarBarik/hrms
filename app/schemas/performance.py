from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class RatingBase(BaseModel):
    rating: float = Field(..., ge=1, le=5)
    category: str
    period_start: date
    period_end: date
    comments: Optional[str] = None

class RatingCreate(RatingBase):
    pass

class RatingUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=5)
    category: Optional[str] = None
    comments: Optional[str] = None

class RatingResponse(RatingBase):
    id: str
    user_id: str
    rated_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ReviewBase(BaseModel):
    review_period: str
    overall_rating: Optional[float] = Field(None, ge=1, le=5)
    achievements: Optional[str] = None
    areas_of_improvement: Optional[str] = None
    goals: Optional[str] = None
    status: str = "draft"

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    overall_rating: Optional[float] = Field(None, ge=1, le=5)
    achievements: Optional[str] = None
    areas_of_improvement: Optional[str] = None
    goals: Optional[str] = None
    status: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    reviewer_id: str
    submitted_at: Optional[datetime]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PerformanceReport(BaseModel):
    average_rating: float
    rating_distribution: dict
    review_completion_rate: float
    department_averages: dict
    top_performers: List[dict]