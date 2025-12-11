from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADING = "UPLOADING"
    INDEXING = "INDEXING"
    ACTIVE = "ACTIVE"
    FAILED = "FAILED"

class FileType(str, enum.Enum):
    PDF = "PDF"
    MP3 = "MP3"
    MP4 = "MP4"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    
    # Path in local storage or GCS (if using intermediate storage)
    local_path = Column(String, nullable=True) 
    
    # ID in Gemini File API
    gemini_file_uri = Column(String, unique=True, nullable=True)
    
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message = Column(String, nullable=True)
    
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    workspace = relationship("Workspace", back_populates="documents")
