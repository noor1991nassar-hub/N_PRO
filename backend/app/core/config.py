import os
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator, computed_field
from typing import Any, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CorporateMemory"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "corporate_memory"
    DATABASE_URL: Optional[str] = None
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # 1. Use explicit DATABASE_URL if set (common in Cloud hosts like Render/Neon)
        if self.DATABASE_URL:
            # Ensure asyncpg driver is used
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://")
            
            # Fix sslmode argument for asyncpg (it expects 'ssl', not 'sslmode')
            if "sslmode=require" in url:
                url = url.replace("sslmode=require", "ssl=require")
                
            return url
            
        # 2. Fallback to SQLite (Local/Default)
        return "sqlite+aiosqlite:///./corporate_memory.db"

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

    class Config:
        case_sensitive = True
        extra = "ignore"
        env_file = ".env"

settings = Settings()
