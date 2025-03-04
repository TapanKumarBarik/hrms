# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pyodbc
import urllib

from app.core.config import settings

# Build connection string for Azure SQL DB
params = urllib.parse.quote_plus(
    f'DRIVER={{{settings.DB_DRIVER}}};'
    f'SERVER={settings.DB_SERVER};'
    f'DATABASE={settings.DB_NAME};'
    f'UID={settings.DB_USER};'
    f'PWD={settings.DB_PASSWORD}'
)

engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={params}",
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()