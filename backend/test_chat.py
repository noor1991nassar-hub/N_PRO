import asyncio
from app.core.database import AsyncSessionLocal
from app.services.rag_service import rag_service
from app.models.tenant import Workspace
from sqlalchemy import select

async def test_chat():
    async with AsyncSessionLocal() as db:
        # Get the workspace
        stmt = select(Workspace).join(Workspace.tenant).where(Workspace.tenant.has(slug="demo-tenant"))
        result = await db.execute(stmt)
        workspace = result.scalars().first()
        
        if not workspace:
            print("Workspace not found!")
            return

        print(f"Testing Chat for Workspace: {workspace.id}")
        query = "Summarize the document"
        print(f"Query: {query}")
        
        try:
            answer = await rag_service.chat_with_workspace(db, workspace.id, query)
            print("-" * 50)
            print("Gemini Answer:")
            print(answer)
            print("-" * 50)
        except Exception as e:
            print(f"Chat failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
