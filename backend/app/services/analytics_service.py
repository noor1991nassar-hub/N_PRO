from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_, desc
from app.models.finance import FinanceInvoice, FinanceInvoiceItem, BankTransaction, ChartOfAccounts, FinanceVendor, VATReport
from app.models.document import Document
from app.models.payroll import PayrollRun
from datetime import datetime


class AnalyticsService:
    async def get_financial_summary(self, db: AsyncSession, tenant_id: int):
        """
        Returns Dashboard 8-KPI Stats.
        """
        stats = {}
        
        # 1. Documents: Last Upload Date
        stmt_docs = select(func.max(Document.upload_date)).where(Document.tenant_id == tenant_id)
        res_docs = await db.execute(stmt_docs)
        stats["last_document_date"] = res_docs.scalar()

        # 2. Records: Last Added Entity Name
        stmt_vendor = select(FinanceVendor.name).where(FinanceVendor.tenant_id == tenant_id).order_by(desc(FinanceVendor.id)).limit(1)
        res_vendor = await db.execute(stmt_vendor)
        stats["last_entity_name"] = res_vendor.scalar()
        
        # 3. Reports: Net Income, Cash Flow, Payments (Last Month)
        # For Demo: Calculate 'All Time' or 'This Month' loosely
        # Revenue
        stmt_rev = select(func.sum(FinanceInvoiceItem.total_price)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoiceItem.gl_code.like("4%")
        )
        total_revenue = (await db.execute(stmt_rev)).scalar() or 0.0
        
        # Expenses
        stmt_exp = select(func.sum(FinanceInvoiceItem.total_price)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoiceItem.gl_code.like("5%")
        )
        total_expenses = (await db.execute(stmt_exp)).scalar() or 0.0
        
        # Payments (Sum of Paid Invoices)
        stmt_paid = select(func.sum(FinanceInvoice.total_amount)).where(
             FinanceInvoice.tenant_id == tenant_id,
             FinanceInvoice.payment_status == 'paid'
        )
        total_payments = (await db.execute(stmt_paid)).scalar() or 0.0

        stats["net_income_last_month"] = total_revenue - total_expenses
        stats["cash_flow_last_month"] = stats["net_income_last_month"] # Simplified Operating CF
        stats["total_payments_last_month"] = total_payments
        
        # 4. Reconciliation: Last Match Date
        stmt_recon = select(func.max(BankTransaction.date)).where(
            BankTransaction.tenant_id == tenant_id,
            BankTransaction.is_reconciled == True
        )
        res_recon = await db.execute(stmt_recon)
        stats["last_reconciliation_date"] = res_recon.scalar()
        
        # 5. Tax: Last Return Date
        stmt_tax = select(func.max(VATReport.period_end)).where(VATReport.tenant_id == tenant_id)
        res_tax = await db.execute(stmt_tax)
        stats["last_tax_return_date"] = res_tax.scalar()
         
        # 6. Payroll: Total Salaries (Last Run)
        # Get latest run payout
        stmt_pay = select(PayrollRun.total_payout).where(PayrollRun.tenant_id == tenant_id).order_by(desc(PayrollRun.id)).limit(1)
        res_pay = await db.execute(stmt_pay)
        stats["total_payroll_last_run"] = res_pay.scalar() or 0.0

        # 7. Tasks: Count of pending tasks
        # We can reuse get_accountant_tasks logic or just do a quick count of unrecon transactions + flagged invoices
        stmt_unrec_count = select(func.count(BankTransaction.id)).where(BankTransaction.tenant_id == tenant_id, BankTransaction.is_reconciled == False)
        unrec_count = (await db.execute(stmt_unrec_count)).scalar() or 0
        
        stmt_flag_count = select(func.count(FinanceInvoice.id)).where(FinanceInvoice.tenant_id == tenant_id, FinanceInvoice.audit_status != "clean")
        flag_count = (await db.execute(stmt_flag_count)).scalar() or 0
        
        stats["pending_tasks_count"] = unrec_count + flag_count

        return stats

    async def get_accountant_tasks(self, db: AsyncSession, tenant_id: int):
        """
        Returns To-Do list for the accountant.
        """
        tasks = []

        # Task 1: Unreconciled Bank Transactions
        stmt_unrec = select(func.count(BankTransaction.id)).where(
            BankTransaction.tenant_id == tenant_id,
            BankTransaction.is_reconciled == False
        )
        res_unrec = await db.execute(stmt_unrec)
        count_unrec = res_unrec.scalar() or 0
        if count_unrec > 0:
            tasks.append({
                "id": "unrec_tx",
                "title": "Unreconciled Transactions",
                "count": count_unrec,
                "severity": "high",
                "description": f"{count_unrec} bank transactions need matching."
            })

        # Task 2: Unclassified Items (Missing GL Code)
        stmt_unclass = select(func.count(FinanceInvoiceItem.id)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            (FinanceInvoiceItem.gl_code == None) | (FinanceInvoiceItem.gl_code == "")
        )
        res_unclass = await db.execute(stmt_unclass)
        count_unclass = res_unclass.scalar() or 0
        if count_unclass > 0:
            tasks.append({
                "id": "unclass_items",
                "title": "Unclassified Items",
                "count": count_unclass,
                "severity": "medium",
                "description": f"{count_unclass} items need GL coding."
            })
            
        # Task 3: Flagged Invoices (Audit)
        # Assuming we check 'audit_status' on invoice
        stmt_flagged = select(func.count(FinanceInvoice.id)).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoice.audit_status != "clean"
        )
        res_flagged = await db.execute(stmt_flagged)
        count_flagged = res_flagged.scalar() or 0
        if count_flagged > 0:
             tasks.append({
                "id": "audit_flags",
                "title": "Audit Flags",
                "count": count_flagged,
                "severity": "high",
                "description": f"{count_flagged} invoices flagged for review."
            })

        return tasks

analytics_service = AnalyticsService()
