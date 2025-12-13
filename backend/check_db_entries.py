import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Get Database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("❌ Error: DATABASE_URL not found in .env")
    exit(1)

# Fix for asyncpg if needed
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
if "sslmode=require" in database_url:
    database_url = database_url.replace("sslmode=require", "ssl=require")

async def check_db():
    print(f"🔌 Connecting to Cloud Database...")
    print(f"   (URL: {database_url.split('@')[1] if '@' in database_url else 'HIDDEN'}...)")
    
    engine = create_async_engine(database_url)
    
    try:
        async with engine.connect() as conn:
            print("✅ Connected!")
            
            # Check Workspaces
            print("\n📂 Workspaces:")
            result = await conn.execute(text("SELECT id, name, created_at FROM workspaces"))
            workspaces = result.fetchall()
            if not workspaces:
                print("   (No workspaces found)")
            for w in workspaces:
                print(f"   - ID: {w.id} | Name: {w.name} | Created: {w.created_at}")

            # Check Documents
            print("\n📄 Documents:")
            result = await conn.execute(text("SELECT id, title, status, gemini_file_uri FROM documents ORDER BY created_at DESC"))
            docs = result.fetchall()
            if not docs:
                print("   (No documents found)")
            for d in docs:
                print(f"   - ID: {d.id}")
                print(f"     Title: {d.title}")
                print(f"     Status: {d.status}")
                print(f"     URI: {d.gemini_file_uri}")
                print("     -------------------------")

    except Exception as e:
        print(f"❌ Database Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
