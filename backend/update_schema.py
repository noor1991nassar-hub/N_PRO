import asyncio
from app.core.database import engine
from app.models.finance import  Base

async def update_schema():
    async with engine.begin() as conn:
        print("Updating Schema (Creating missing tables)...")
        await conn.run_sync(Base.metadata.create_all)
        print("Schema Update Complete.")

if __name__ == "__main__":
    asyncio.run(update_schema())
