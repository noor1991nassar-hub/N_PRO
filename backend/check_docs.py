import asyncio
from app.core.database import AsyncSessionLocal
from app.models.document import Document
from sqlalchemy import select

async def check_docs():
    async with AsyncSessionLocal() as db:
        stmt = select(Document)
        result = await db.execute(stmt)
        docs = result.scalars().all()
        
        print(f"Total Documents: {len(docs)}")
        for doc in docs:
            print(f"ID: {doc.id} | Title: {doc.title} | Status: {doc.status} | URI: {doc.gemini_file_uri}")

if __name__ == "__main__":
    asyncio.run(check_docs())
