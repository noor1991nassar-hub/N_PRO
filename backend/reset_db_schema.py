import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
if "sslmode=require" in database_url:
    database_url = database_url.replace("sslmode=require", "ssl=require")

async def reset_db():
    print("⚠️  WARNING: DROPPING ALL TABLES IN DATABASE...")
    print(f"Target: {database_url.split('@')[1] if '@' in database_url else 'HIDDEN'}")
    
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS revisions CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS documents CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS workspaces CASCADE;")) # Old table
            await conn.execute(text("DROP TABLE IF EXISTS tenants CASCADE;"))
            
        print("✅ All tables dropped successfully.")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_db())
