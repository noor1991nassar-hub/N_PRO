import asyncio
from app.core.database import AsyncSessionLocal
from app.models.document import Document
from sqlalchemy import delete

async def reset_documents():
    async with AsyncSessionLocal() as db:
        print("Clearing all documents...")
        await db.execute(delete(Document))
        await db.commit()
        print("Documents cleared.")

if __name__ == "__main__":
    asyncio.run(reset_documents())
