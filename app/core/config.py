# app/core/config.py
import os
from pydantic import BaseSettings
from typing import List
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HRMS API"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://yourfrontend.azurewebsites.net"
    ]

    # Database
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER: str = os.getenv("DB_SERVER", "your-server.database.windows.net")
    DB_NAME: str = os.getenv("DB_NAME", "hrms")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    
    
    def get_connection_string(self) -> str:
        conn_str = f"DRIVER={{{self.DB_DRIVER}}};SERVER={self.DB_SERVER};DATABASE={self.DB_NAME};UID={self.DB_USER};PWD={self.DB_PASSWORD}"
        return f"mssql+pyodbc:///?odbc_connect={quote_plus(conn_str)}"


settings = Settings()

