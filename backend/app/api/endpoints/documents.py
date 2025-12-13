from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_tenant_id
from app.services.rag_service import rag_service
from app.models.tenant import Tenant
from app.models.document import Document
from sqlalchemy import select

router = APIRouter()

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    """
    Upload a document for the current tenant.
    """
    # 1. Resolve Tenant (Lazy Seed)
    # Use the header value, or fall back to "Construction Corp" if generic
    target_name = tenant_name if tenant_name else "Construction Corp"
    
    stmt = select(Tenant).where(Tenant.company_name == target_name)
    result = await db.execute(stmt)
    tenant = result.scalars().first()
    
    # Auto-create (Lazy Seeding) if missing - preventing "Tenant not found" in demos
    if not tenant:
        tenant = Tenant(
            company_name=target_name,
            subscription_status=True,
            subscribed_modules=["finance", "engineer"]
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

    # 2. Upload Document
    document = await rag_service.upload_document(db, file, tenant.id)
    return {"id": document.id, "title": document.filename, "status": document.status}

@router.get("/document")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    """
    List all documents for the current tenant.
    """
    # 1. Resolve Tenant
    stmt = select(Tenant).where(Tenant.company_name == "Construction Corp")
    result = await db.execute(stmt)
    tenant = result.scalars().first()
    
    if not tenant:
         raise HTTPException(status_code=404, detail="Tenant not found.")
    
    # 2. Sync status with Gemini (Optional but good for UX)
    from app.services.gemini import gemini_service
    
    stmt = select(Document).where(Document.tenant_id == tenant.id).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    docs = result.scalars().all()
    
    # Check status (Simplified for stability logic, avoiding too much logic in controller)
    # Ideally should be a background task or separate syncer
    for d in docs:
        if d.status == "processing" and d.file_uri:
            try:
                # URI format assumption: https://.../files/xxxx
                if "/files/" in d.file_uri:
                    file_name = "files/" + d.file_uri.split("/files/")[-1]
                    
                    state = await gemini_service.get_file_state(file_name)
                    if state == "ACTIVE":
                        d.status = "active"
                        db.add(d)
                        await db.commit()
                    elif state == "FAILED":
                        d.status = "failed"
                        db.add(d)
                        await db.commit()
            except Exception as e:
                # Log error but don't break listing
                pass
    
    return [{"id": d.id, "title": d.filename, "status": d.status, "created_at": d.created_at} for d in docs]
