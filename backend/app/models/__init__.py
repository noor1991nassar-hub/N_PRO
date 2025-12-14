from app.models.tenant import Tenant, User, UserRole
from app.models.document import Document
from app.models.finance import (
    FinanceVendor, FinanceInvoice, FinanceInvoiceItem, FinanceAuditFlag,
    ChartOfAccounts, BankTransaction, VATReport
)
# Assuming these exist in payroll.py
try:
    from app.models.payroll import Employee, EmploymentContract, PayrollRun, PayrollSlip
except ImportError:
    pass # Handle if payroll module is not ready yet, but seed script uses it
