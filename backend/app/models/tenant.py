from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from app.core.database import Base
import enum

# Define the 4 Verticals + Admin
class UserRole(str, enum.Enum):
    ADMIN = "admin"           # System Admin / Company Manager
    ENGINEER = "engineer"     # Engineering & Construction Vertical
    LAWYER = "lawyer"         # Legal Vertical
    ACCOUNTANT = "accountant" # Finance Vertical
    HR = "hr"                 # Human Resources Vertical

class Tenant(Base):
    """
    Represents the Client Company (The Organization).
    """
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    # Changed from 'name'/'slug' to 'company_name' as per user request
    company_name = Column(String, index=True)
    
    # AI Configuration per Tenant
    gemini_api_key = Column(String, nullable=True) # If null, use system default
    ai_config = Column(JSON, default={"tone": "professional", "language": "ar"})
    
    # Subscription Details
    subscription_status = Column(Boolean, default=True)
    # List of allowed verticals e.g., ["engineer", "lawyer"]
    subscribed_modules = Column(JSON, default=list) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    """
    Represents the Employee within a Company.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String) # Essential for AI personalization
    
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    role = Column(String, default=UserRole.ENGINEER) # Determines Access Rights
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
