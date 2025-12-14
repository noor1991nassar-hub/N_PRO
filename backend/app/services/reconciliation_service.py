from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from datetime import timedelta
from app.models.finance import BankTransaction, FinanceInvoice
import logging

logger = logging.getLogger(__name__)

class ReconciliationService:
    async def auto_reconcile(self, db: AsyncSession, tenant_id: int):
        """
        Auto-matches Bank Transactions to Invoices.
        Criteria:
        1. Exact Amount Match
        2. Date within +/- 7 days
        """
        # 1. Fetch Unreconciled Transactions (Negative amounts usually = Expenses/Payments)
        # Note: Invoices are usually positive totals. Bank withdrawals are negative.
        # We need to flip the sign or assume user input is normalized. 
        # Let's assume BankTransaction.amount for withdrawals is NEGATIVE.
        
        stmt = select(BankTransaction).where(
            BankTransaction.tenant_id == tenant_id,
            BankTransaction.is_reconciled == False
        )
        result = await db.execute(stmt)
        transactions = result.scalars().all()
        
        matches_found = 0
        
        for tx in transactions:
            # Target amount: abs(tx.amount) because invoice total is positive
            target_amount = abs(tx.amount)
            
            # Date Range
            min_date = tx.date - timedelta(days=7)
            max_date = tx.date + timedelta(days=7)
            
            # Find candidate invoices
            # - Unpaid or Pending Reconciliation? 
            # - Matching Amount
            # - Matching Date Range
            stmt_inv = select(FinanceInvoice).where(
                FinanceInvoice.tenant_id == tenant_id,
                FinanceInvoice.total_amount == target_amount,
                FinanceInvoice.invoice_date >= min_date,
                FinanceInvoice.invoice_date <= max_date,
                # Avoid already reconciled? We don't have a direct link on Invoice yet 
                # but we can check if it's already linked? 
                # For MVP, let's just find one.
            )
            res_inv = await db.execute(stmt_inv)
            candidate = res_inv.scalars().first()
            
            if candidate:
                # MATCH FOUND!
                tx.is_reconciled = True
                tx.matched_invoice_id = candidate.id
                tx.match_confidence = 0.95 # High confidence due to exact amount + date
                
                # Update Invoice? 
                candidate.payment_status = "Paid" # Assume reconciled means paid
                
                db.add(tx)
                db.add(candidate)
                matches_found += 1
                logger.info(f"Reconciled Tx {tx.id} with Invoice {candidate.id}")
        
        await db.commit()
        return {"matches": matches_found, "processed": len(transactions)}

    async def create_dummy_bank_transactions(self, db: AsyncSession, tenant_id: int):
        """
        Seeds some dummy transactions for testing reconciliation.
        """
        from datetime import datetime, timedelta
        
        # Create a tx that matches an invoice if any exist
        stmt = select(FinanceInvoice).where(FinanceInvoice.tenant_id == tenant_id).limit(1)
        res = await db.execute(stmt)
        inv = res.scalars().first()
        
        if inv:
            # Create a matching withdrawal
            tx = BankTransaction(
                tenant_id=tenant_id,
                date=inv.invoice_date + timedelta(days=2), # Paid 2 days later
                description=f"Payment for {inv.invoice_number}",
                amount=-inv.total_amount, # Negative for withdrawal
                reference_number="REF-12345",
                is_reconciled=False
            )
            db.add(tx)
            await db.commit()
            return "Created matching dummy transaction."
        return "No invoices to match against."

reconciliation_service = ReconciliationService()
