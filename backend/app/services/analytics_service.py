from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_
from app.models.finance import FinanceInvoice, FinanceInvoiceItem, BankTransaction, ChartOfAccounts

class AnalyticsService:
    async def get_financial_summary(self, db: AsyncSession, tenant_id: int):
        """
        Calculates P&L and Budget usage.
        Income Statement: Sum(Revenue) - Sum(Expense)
        """
        # 1. Total Expenses (Items linked to 5xxx codes)
        # We need to join InvoiceItem -> COA or just filter by gl_code starting with '5'
        
        # Expenses
        stmt_expenses = select(func.sum(FinanceInvoiceItem.total_price)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoiceItem.gl_code.like("5%")
        )
        expenses_result = await db.execute(stmt_expenses)
        total_expenses = expenses_result.scalar() or 0.0

        # Revenue (Items linked to 4xxx codes) - Assuming we track sales invoices too? 
        # For now, if we only process verify expenses, revenue might be 0 or manual.
        # User prompt says "Sum(Revenue 4xxx)". Let's implement logic.
        stmt_revenue = select(func.sum(FinanceInvoiceItem.total_price)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoiceItem.gl_code.like("4%")
        )
        revenue_result = await db.execute(stmt_revenue)
        total_revenue = revenue_result.scalar() or 0.0

        net_income = total_revenue - total_expenses

        # Budget (Mock or Calculated)
        # For now, let's hardcode a simple budget limit for demo
        budget_limit = 50000.0 # Example
        budget_usage = (total_expenses / budget_limit) * 100 if budget_limit > 0 else 0

        return {
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_income": net_income,
            "budget_limit": budget_limit,
            "budget_usage_percent": round(budget_usage, 1)
        }

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
