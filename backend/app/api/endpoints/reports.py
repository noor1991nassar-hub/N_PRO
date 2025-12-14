from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.core.database import get_db
from app.models.finance import FinanceInvoice, FinanceVendor, ChartOfAccounts, FinanceInvoiceItem
# Assuming get_current_tenant_id is the standard dependency we use for tenancy
from app.api.deps import get_current_tenant_id
from typing import List, Optional
from datetime import datetime, timedelta

router = APIRouter()

# --- Zone 2: Financial Statements Data ---
@router.get("/financial-statements")
def get_financial_statements(
    period: str = "this_year", 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    # 1. Determine Date Range
    now = datetime.now()
    if period == "this_month":
        start_date = now.replace(day=1)
    elif period == "this_quarter":
        quarter = (now.month - 1) // 3 + 1
        start_date = datetime(now.year, 3 * quarter - 2, 1)
    else: # this_year
        start_date = datetime(now.year, 1, 1)
        
    # 2. Calculate P&L (Revenue - Expenses)
    # Logic: Sum items based on Chart of Accounts Type
    # Note: actual filter should also consider invoice_date >= start_date
    
    revenue = db.query(func.sum(FinanceInvoiceItem.total_price))\
        .join(ChartOfAccounts, FinanceInvoiceItem.gl_code == ChartOfAccounts.code)\
        .join(FinanceInvoice)\
        .filter(ChartOfAccounts.account_type == "Revenue")\
        .filter(FinanceInvoice.invoice_date >= start_date)\
        .scalar() or 0
        
    expenses = db.query(func.sum(FinanceInvoiceItem.total_price))\
        .join(ChartOfAccounts, FinanceInvoiceItem.gl_code == ChartOfAccounts.code)\
        .join(FinanceInvoice)\
        .filter(ChartOfAccounts.account_type == "Expense")\
        .filter(FinanceInvoice.invoice_date >= start_date)\
        .scalar() or 0
        
    # 3. Calculate Balance Sheet (Assets vs Liabilities) - Usually Cumulative, but simpler metric here
    assets = db.query(func.sum(FinanceInvoiceItem.total_price))\
        .join(ChartOfAccounts, FinanceInvoiceItem.gl_code == ChartOfAccounts.code)\
        .filter(ChartOfAccounts.account_type == "Asset")\
        .scalar() or 0
        
    liabilities = db.query(func.sum(FinanceInvoiceItem.total_price))\
        .join(ChartOfAccounts, FinanceInvoiceItem.gl_code == ChartOfAccounts.code)\
        .filter(ChartOfAccounts.account_type == "Liability")\
        .scalar() or 0

    return {
        "net_income": revenue - expenses,
        "revenue": revenue,
        "expenses": expenses,
        "total_assets": assets,
        "total_liabilities": liabilities,
        "equity": assets - liabilities 
    }

# --- Zone 3: Entity Explorer Data ---
@router.get("/entities")
def get_entities_summary(
    type: str = "vendor", 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    # Returns list of Vendors with calculated totals (Total Billed, Paid, Due)
    
    # Aggregate invoices by Vendor
    results = db.query(
        FinanceVendor.id,
        FinanceVendor.name,
        func.sum(FinanceInvoice.total_amount).label("total_billed"),
        func.sum(case((FinanceInvoice.payment_status == 'paid', FinanceInvoice.total_amount), else_=0)).label("total_paid")
    ).join(FinanceInvoice).group_by(FinanceVendor.id).all()
    
    entities = []
    for r in results:
        balance_due = (r.total_billed or 0) - (r.total_paid or 0)
        entities.append({
            "id": r.id,
            "name": r.name,
            "total_billed": r.total_billed or 0,
            "total_paid": r.total_paid or 0,
            "balance_due": balance_due,
            "status": "Active" if balance_due < 1000 else "Payment Pending"
        })
    return entities

@router.get("/entity/{entity_id}/ledger")
def get_entity_ledger(
    entity_id: int, 
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id)
):
    # Returns last 10 transactions for the "Entity Card"
    invoices = db.query(FinanceInvoice).filter(FinanceInvoice.vendor_id == entity_id)\
        .order_by(FinanceInvoice.invoice_date.desc()).limit(10).all()
    return invoices
