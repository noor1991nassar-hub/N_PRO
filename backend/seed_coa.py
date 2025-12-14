import asyncio
from sqlalchemy import select
from app.models.finance import ChartOfAccounts, Base
from app.core.database import AsyncSessionLocal, engine

async def seed_chart_of_accounts():
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        
        # Based on the user's provided image
        accounts = [
            # Assets (1000-1999) -> Balance Sheet
            {"code": "1000", "name": "Cash", "type": "Asset"},
            {"code": "1200", "name": "Inventory", "type": "Asset"},
            {"code": "1400", "name": "Fixed Assets", "type": "Asset"}, # Computers, Furniture
            
            # Liabilities (2000-2999) -> Balance Sheet
            {"code": "2000", "name": "Accounts Payable", "type": "Liability"},
            
            # Equity (3000-3999) -> Balance Sheet
            {"code": "3000", "name": "Owner's Equity", "type": "Equity"},
            
            # Revenue (4000-4999) -> Income Statement
            {"code": "4000", "name": "Sales Revenue", "type": "Revenue"},
            
            # Expenses (5000-5999) -> Income Statement
            {"code": "5000", "name": "Cost of Goods Sold", "type": "Expense"},
            {"code": "5100", "name": "Salaries and Wages", "type": "Expense"},
            {"code": "5200", "name": "Rent Expense", "type": "Expense"},
            {"code": "5300", "name": "Utilities Expense", "type": "Expense"},
            {"code": "5400", "name": "Marketing Expense", "type": "Expense"},
            {"code": "5500", "name": "General Admin Expenses", "type": "Expense"},
        ]

        try:
            print("Starting Seed...")
            for acc in accounts:
                stmt = select(ChartOfAccounts).where(ChartOfAccounts.code == acc["code"])
                result = await db.execute(stmt)
                exists = result.scalars().first()
                
                if not exists:
                    new_acc = ChartOfAccounts(
                        code=acc["code"], 
                        name=acc["name"], 
                        account_type=acc["type"]
                    )
                    db.add(new_acc)
                    print(f"Added: {acc['code']} - {acc['name']}")
                else:
                    print(f"Skipped: {acc['code']} (Exists)")
            
            await db.commit()
            print("Chart of Accounts Seeded Successfully!")
        except Exception as e:
            print(f"Error seeding COA: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(seed_chart_of_accounts())
