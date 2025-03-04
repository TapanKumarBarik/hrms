from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from statistics import mean

from app.db.session import get_db
from app.db import models
from app.schemas.performance import (
    RatingCreate, RatingUpdate, RatingResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse,
    PerformanceReport
)
from app.core.auth import get_current_user_with_permissions

router = APIRouter()

@router.get("/employees/{employee_id}/ratings", response_model=List[RatingResponse])
async def check_ratings(
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if (current_user.id != employee_id and 
        current_user.role.name not in ["Manager", "HR", "Admin"] and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == employee_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    ratings = db.query(models.PerformanceRating).filter(
        models.PerformanceRating.user_id == employee_id
    ).all()
    return ratings

@router.post("/employees/{employee_id}/ratings", response_model=RatingResponse)
async def submit_rating(
    employee_id: str,
    rating_data: RatingCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    rating = models.PerformanceRating(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        rated_by=current_user.id,
        **rating_data.dict()
    )
    
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating

@router.put("/employees/{employee_id}/ratings/{rating_id}", 
           response_model=RatingResponse)
async def update_rating(
    employee_id: str,
    rating_id: str,
    rating_data: RatingUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    rating = db.query(models.PerformanceRating).filter(
        models.PerformanceRating.id == rating_id,
        models.PerformanceRating.user_id == employee_id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    for key, value in rating_data.dict(exclude_unset=True).items():
        setattr(rating, key, value)

    db.commit()
    db.refresh(rating)
    return rating

@router.delete("/employees/{employee_id}/ratings/{rating_id}")
async def delete_rating(
    employee_id: str,
    rating_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    rating = db.query(models.PerformanceRating).filter(
        models.PerformanceRating.id == rating_id,
        models.PerformanceRating.user_id == employee_id
    ).first()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    db.delete(rating)
    db.commit()
    return {"message": "Rating deleted successfully"}

@router.get("/employees/{employee_id}/reviews", response_model=List[ReviewResponse])
async def get_performance_reviews(
    employee_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if (current_user.id != employee_id and 
        current_user.role.name not in ["Manager", "HR", "Admin"] and
        not db.query(models.User).filter(
            models.User.manager_id == current_user.id,
            models.User.id == employee_id
        ).first()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    reviews = db.query(models.PerformanceReview).filter(
        models.PerformanceReview.user_id == employee_id
    ).all()
    return reviews

@router.post("/employees/{employee_id}/reviews", response_model=ReviewResponse)
async def submit_performance_review(
    employee_id: str,
    review_data: ReviewCreate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    review = models.PerformanceReview(
        id=str(uuid.uuid4()),
        user_id=employee_id,
        reviewer_id=current_user.id,
        submitted_at=datetime.utcnow() if review_data.status == "submitted" else None,
        **review_data.dict()
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.put("/employees/{employee_id}/reviews/{review_id}", 
           response_model=ReviewResponse)
async def update_performance_review(
    employee_id: str,
    review_id: str,
    review_data: ReviewUpdate,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    review = db.query(models.PerformanceReview).filter(
        models.PerformanceReview.id == review_id,
        models.PerformanceReview.user_id == employee_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    if review_data.status == "submitted":
        review_data.submitted_at = datetime.utcnow()
    elif review_data.status == "approved":
        review_data.approved_at = datetime.utcnow()

    for key, value in review_data.dict(exclude_unset=True).items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)
    return review

@router.delete("/employees/{employee_id}/reviews/{review_id}")
async def delete_performance_review(
    employee_id: str,
    review_id: str,
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    review = db.query(models.PerformanceReview).filter(
        models.PerformanceReview.id == review_id,
        models.PerformanceReview.user_id == employee_id
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}

@router.get("/performance/reports", response_model=PerformanceReport)
async def generate_performance_reports(
    current_user: models.User = Depends(get_current_user_with_permissions),
    db: Session = Depends(get_db)
):
    if current_user.role.name not in ["Manager", "HR", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Calculate overall statistics
    ratings = db.query(models.PerformanceRating).all()
    all_ratings = [r.rating for r in ratings]
    
    rating_distribution = {}
    for rating in range(1, 6):
        rating_distribution[rating] = len([r for r in all_ratings if r == rating])

    # Calculate department averages
    dept_ratings = {}
    departments = db.query(models.Department).all()
    for dept in departments:
        dept_users = db.query(models.User).filter(
            models.User.department_id == dept.id
        ).all()
        dept_user_ids = [u.id for u in dept_users]
        dept_ratings[dept.name] = mean(
            [r.rating for r in ratings if r.user_id in dept_user_ids]
        ) if ratings else 0

    # Get top performers
    top_performers = (
        db.query(models.User)
        .join(models.PerformanceRating)
        .group_by(models.User.id)
        .order_by(db.func.avg(models.PerformanceRating.rating).desc())
        .limit(5)
        .all()
    )

    return PerformanceReport(
        average_rating=mean(all_ratings) if all_ratings else 0,
        rating_distribution=rating_distribution,
        review_completion_rate=0.85,  # Example - implement actual calculation
        department_averages=dept_ratings,
        top_performers=[{"id": user.id, "name": user.name} for user in top_performers]
    )