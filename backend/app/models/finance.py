from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, func
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

# --- 2. Bank Transactions (For Reconciliation) ---
class BankTransaction(Base):
    __tablename__ = "bank_transactions"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    date = Column(DateTime)
    description = Column(String)
    amount = Column(Float) # Negative = Withdrawal
    reference_number = Column(String, nullable=True)
    
    # Reconciliation Status
    is_reconciled = Column(Boolean, default=False)
    matched_invoice_id = Column(Integer, ForeignKey("finance_invoices.id"), nullable=True)
    match_confidence = Column(Float, default=0.0) 

    tenant = relationship("Tenant")
    matched_invoice = relationship("FinanceInvoice")

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

# --- New Model: The Standard Chart of Accounts ---
class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True) # e.g., "1000", "5100"
    name = Column(String) # e.g., "Cash", "Rent Expense"
    
    # Type determines where it goes: "Balance Sheet" or "Income Statement"
    # "Asset", "Liability", "Equity", "Revenue", "Expense"
    account_type = Column(String) 

class FinanceInvoiceItem(Base):
    __tablename__ = "finance_invoice_items"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("finance_invoices.id"))
    
    description = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    category = Column(String) # AI Classified (e.g., "Marketing", "Utilities")

    # --- New Accounting Fields ---
    # The AI will select the best GL Code for this item
    gl_code = Column(String, ForeignKey("chart_of_accounts.code"), nullable=True) 
    
    # "Debit" or "Credit" (Expenses/Assets are usually Debit)
    entry_type = Column(String, default="Debit") 
    
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

class VATReport(Base):
    __tablename__ = "vat_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    total_sales = Column(Float)
    total_sales_vat = Column(Float) # Output Tax
    
    total_purchases = Column(Float)
    total_purchases_vat = Column(Float) # Input Tax
    
    net_vat_payable = Column(Float) # The amount to pay to ZATCA
    
    status = Column(String, default="Draft") # Draft, Submitted, Paid
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tenant = relationship("Tenant")
