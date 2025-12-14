import asyncio
from sqlalchemy import select, func
from app.core.database import AsyncSessionLocal
from app.models.finance import FinanceInvoice, FinanceInvoiceItem

async def check_data():
    async with AsyncSessionLocal() as db:
        # Count Invoices
        result = await db.execute(select(func.count(FinanceInvoice.id)))
        invoice_count = result.scalar()
        
        # Count Items
        result = await db.execute(select(func.count(FinanceInvoiceItem.id)))
        item_count = result.scalar()
        
        print(f"--- DB STATUS ---")
        print(f"Invoices: {invoice_count}")
        print(f"Line Items: {item_count}")
        
        # List last invoice details
        stmt = select(FinanceInvoice).order_by(FinanceInvoice.id.desc()).limit(1)
        result = await db.execute(stmt)
        last_inv = result.scalars().first()
        
        if last_inv:
            print(f"Last Invoice ID: {last_inv.id}, Vendor: {last_inv.vendor_id}, Total: {last_inv.total_amount}")

if __name__ == "__main__":
    asyncio.run(check_data())
