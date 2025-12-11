from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_tenant_id
from app.services.rag_service import rag_service
from app.models.tenant import Workspace
from sqlalchemy import select
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

@router.post("/chat")
async def chat_with_docs(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    # Resolve Workspace
    stmt = select(Workspace).join(Workspace.tenant).where(Workspace.tenant.has(slug=tenant_id))
    result = await db.execute(stmt)
    workspace = result.scalars().first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    answer = await rag_service.chat_with_workspace(db, workspace.id, request.query)
    return {"answer": answer}
