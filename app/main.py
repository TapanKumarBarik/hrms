# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
import os
from dotenv import load_dotenv

from app.routers import users,auth
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import engine
from app.db import models
from app.routers import leaves
from app.routers import salary
from app.routers import courses
from app.routers import certifications
from app.routers import onboarding
from app.routers import policies
from app.routers import benefits
from app.routers import performance
from app.routers import projects
from app.routers import attendance

# Load environment variables
load_dotenv()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HRMS API",
    description="Human Resource Management System API",
    version="1.0.0"
)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(leaves.router, prefix="/api/v1", tags=["leaves"])
app.include_router(salary.router, prefix="/api/v1", tags=["salary"])
app.include_router(courses.router, prefix="/api/v1", tags=["courses"])
app.include_router(certifications.router, prefix="/api/v1", tags=["certifications"])
app.include_router(onboarding.router, prefix="/api/v1", tags=["onboarding"])
app.include_router(policies.router, prefix="/api/v1", tags=["policies"])
app.include_router(benefits.router, prefix="/api/v1", tags=["benefits"])
app.include_router(performance.router, prefix="/api/v1", tags=["performance"])
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(attendance.router, prefix="/api/v1", tags=["attendance"])

@app.get("/")
def root():
    return {"message": "Welcome to HRMS API. See /docs for API documentation."}