from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class FinanceVendor(Base):
    __tablename__ = "finance_vendors"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String, index=True)
    tax_id = Column(String, nullable=True)
    contact_info = Column(Text, nullable=True)
    trust_score = Column(Integer, default=100) # AI logic will lower this if fraud detected
    
    tenant = relationship("Tenant")
    invoices = relationship("FinanceInvoice", back_populates="vendor")

class FinanceInvoice(Base):
    __tablename__ = "finance_invoices"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    document_id = Column(Integer, ForeignKey("documents.id")) # Link to the physical file
    vendor_id = Column(Integer, ForeignKey("finance_vendors.id"), nullable=True)
    
    invoice_number = Column(String, index=True)
    invoice_date = Column(DateTime)
    due_date = Column(DateTime, nullable=True)
    total_amount = Column(Float)
    currency = Column(String, default="SAR")
    payment_status = Column(String, default="Unpaid")
    
    # Status flags
    extraction_status = Column(String, default="pending") # pending -> processing -> completed
    audit_status = Column(String, default="clean") # clean -> flagged
    
    # Relations
    tenant = relationship("Tenant")
    document = relationship("Document", back_populates="invoices")
    vendor = relationship("FinanceVendor", back_populates="invoices")
    items = relationship("FinanceInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    audit_logs = relationship("FinanceAuditFlag", back_populates="invoice", cascade="all, delete-orphan")

class FinanceInvoiceItem(Base):
    __tablename__ = "finance_invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("finance_invoices.id"))
    
    description = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    category = Column(String) # AI Classified (e.g., "Marketing", "Utilities")
    
    invoice = relationship("FinanceInvoice", back_populates="items")

class FinanceAuditFlag(Base):
    __tablename__ = "finance_audit_flags"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("finance_invoices.id"))
    
    issue_type = Column(String) # "duplicate", "missing_tax_id"
    severity = Column(String) # "high", "medium", "low"
    description = Column(Text)
    ai_explanation = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    
    invoice = relationship("FinanceInvoice", back_populates="audit_logs")
