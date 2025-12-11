from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_tenant_id
from app.services.rag_service import rag_service
from app.models.tenant import Workspace 
from sqlalchemy import select

router = APIRouter()

@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """
    Upload a document to the current tenant's default workspace.
    """
    # 1. Resolve Workspace (Simplified: Get first workspace for tenant)
    # In real app, workspace_id should be passed or resolved from context
    stmt = select(Workspace).join(Workspace.tenant).where(Workspace.tenant.has(slug=tenant_id))
    result = await db.execute(stmt)
    workspace = result.scalars().first()
    
    if not workspace:
        # Auto-create default workspace if missing (for demo purposes)
        # In production this should be 404
        pass 
        # For now, let's assume we need a workspace ID passed or we fail.
        # But to make the demo smoother, we will check if we can query by just tenant.
        # Let's fail for now if no workspace found to enforce correct setup.
        # raise HTTPException(status_code=404, detail="No workspace found for this tenant")
        
        # ACTUALLY: Let's create a Mock Workspace Logic here if we don't have DB populated
        # This is risky without DB migration run. 
        # But we will write the code assuming DB is ready.
    
    # Bypass DB check for strictly "Code Scaffolding" phase if DB is down?
    # No, we wrote the code to use DB.
    
    if not workspace:
         raise HTTPException(status_code=404, detail="Workspace not found. Please assure tenant setup.")

    document = await rag_service.upload_document(db, file, workspace.id)
    return {"id": document.id, "title": document.title, "status": document.status}

@router.get("/document")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """
    List all documents in the current tenant's default workspace.
    """
    stmt = select(Workspace).join(Workspace.tenant).where(Workspace.tenant.has(slug=tenant_id))
    result = await db.execute(stmt)
    workspace = result.scalars().first()
    
    if not workspace:
         raise HTTPException(status_code=404, detail="Workspace not found.")
    
    # Sync status with Gemini for documents that are still indexing
    from app.models.document import Document, ProcessingStatus
    from app.services.gemini import gemini_service
    
    stmt = select(Document).where(Document.workspace_id == workspace.id).order_by(Document.created_at.desc())
    result = await db.execute(stmt)
    docs = result.scalars().all()
    
    for d in docs:
        if d.status == ProcessingStatus.INDEXING and d.gemini_file_uri:
            try:
                # Extract 'files/xxx' from URI. 
                # URI format assumption: https://.../files/xxxx
                if "/files/" in d.gemini_file_uri:
                    file_name = "files/" + d.gemini_file_uri.split("/files/")[-1]
                    
                    state = await gemini_service.get_file_state(file_name)
                    if state == "ACTIVE":
                        d.status = ProcessingStatus.ACTIVE
                        db.add(d)
                        await db.commit()
                        await db.refresh(d)
                    elif state == "FAILED":
                        d.status = ProcessingStatus.FAILED
                        db.add(d)
                        await db.commit()
            except Exception as e:
                # Log error but don't break listing
                print(f"Error syncing doc {d.id}: {e}")
                pass
    
    return [{"id": d.id, "title": d.title, "status": d.status, "created_at": d.created_at} for d in docs]
