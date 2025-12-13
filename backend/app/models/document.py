from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Document(Base):
    """
    Represents Uploaded Knowledge Base.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    filename = Column(String)
    file_uri = Column(String) # Google Gemini File URI
    
    # Security: Which vertical can see this file?
    # e.g., "engineer" (only engineers see this), or "general" (everyone sees it)
    access_level = Column(String, default="general") 
    
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="indexing")
    
    tenant = relationship("Tenant", back_populates="documents")

    @property
    def title(self):
        return self.filename

    @property
    def created_at(self):
        return self.upload_date

    @property
    def gemini_file_uri(self):
        return self.file_uri
