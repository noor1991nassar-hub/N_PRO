from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_tenant_id
from app.services.rag_service import rag_service
from app.models.tenant import Tenant, User
from sqlalchemy import select
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    user_email: str = "eng@demo.com" # Default to Engineer for demo

@router.post("/chat")
async def chat_with_docs(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    # 1. Resolve Tenant
    stmt = select(Tenant).where(Tenant.company_name == "Construction Corp")
    result = await db.execute(stmt)
    tenant = result.scalars().first()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 2. Resolve User (Simulated Auth)
    stmt = select(User).where(User.email == request.user_email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        # Fallback dump user
        raise HTTPException(status_code=401, detail="User not identified")
        
    # 3. Chat with Vertical Context
    answer = await rag_service.chat_with_tenant(db, tenant.id, user, request.query)
    return {"answer": answer, "role_used": user.role}
