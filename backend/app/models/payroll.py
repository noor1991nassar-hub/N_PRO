from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    name = Column(String)
    national_id = Column(String) # For WPS
    iban = Column(String)        # For Bank Transfer
    email = Column(String)
    
    # Relationships
    tenant = relationship("Tenant")
    contract = relationship("EmploymentContract", uselist=False, back_populates="employee")
    payslips = relationship("PayrollSlip", back_populates="employee")

class EmploymentContract(Base):
    __tablename__ = "employment_contracts"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    
    # Salary Breakdown (Saudi Standard)
    basic_salary = Column(Float, default=0.0)
    housing_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    other_allowance = Column(Float, default=0.0)
    
    gosi_deduction_rate = Column(Float, default=0.0975) # Standard GOSI
    
    start_date = Column(DateTime)
    document_uri = Column(String) # Link to PDF Contract
    
    employee = relationship("Employee", back_populates="contract")

class PayrollRun(Base):
    __tablename__ = "payroll_runs"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    
    month = Column(Integer) # e.g., 5
    year = Column(Integer)  # e.g., 2025
    total_payout = Column(Float)
    status = Column(String, default="Draft") # Draft -> Approved -> Paid
    
    tenant = relationship("Tenant")
    slips = relationship("PayrollSlip", back_populates="run")

class PayrollSlip(Base):
    __tablename__ = "payroll_slips"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("payroll_runs.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    
    # Calculated Figures
    gross_salary = Column(Float)
    absent_days = Column(Integer, default=0)
    deduction_amount = Column(Float, default=0.0)
    net_salary = Column(Float)
    
    run = relationship("PayrollRun", back_populates="slips")
    employee = relationship("Employee", back_populates="payslips")
