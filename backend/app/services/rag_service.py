from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile, HTTPException
from app.models.document import Document
from app.models.tenant import Tenant, User
from app.models.finance import FinanceInvoice, FinanceInvoiceItem, FinanceAuditFlag
from sqlalchemy import select, delete, text
from sqlalchemy.orm import selectinload
from app.services.gemini import gemini_service
import shutil
import os
import uuid

# Temp storage for uploaded files before sending to Gemini
UPLOAD_DIR = "backend/temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RAGService:
    async def upload_document(self, db: AsyncSession, file: UploadFile, tenant_id: int, force: bool = False):
        """
        Vertical SaaS Upload:
        - Linked to Tenant (not Workspace).
        - Default Access: General (for now, can be parameterized).
        """
        # 0. Check for Duplicates (Gemini Level)
        # We check by filename for simplicity in this MVP
        existing_file = await gemini_service.check_file_exists(file.filename)
        
        if existing_file:
            if not force:
                # Return 409 Conflict so Frontend can prompt user
                raise HTTPException(
                    status_code=409, 
                    detail=f"File '{file.filename}' already exists.",
                    headers={"X-Duplicate-Of": existing_file.name}
                )
            else:
                # Force Overwrite: Delete old file from Gemini & DB
                print(f"DEBUG: Force Overwrite triggered for {existing_file.name}")
                try:
                    await gemini_service.delete_file(existing_file.name)
                    print(f"DEBUG: Gemini file deleted")
                except Exception as e:
                    print(f"DEBUG: Gemini delete failed (ignoring): {e}")

                try:
                    # Clean up DB (Raw SQL "Nuclear Option")
                    # Bypass ORM session cache to ensure deletion propagates to DB immediately
                    stmt = select(Document).where(Document.file_uri == existing_file.uri)
                    result = await db.execute(stmt)
                    old_doc = result.scalars().first()
                    
                    if old_doc:
                        doc_id = old_doc.id
                        print(f"DEBUG: Found old doc {doc_id}, executing RAW SQL delete")
                        
                        # Use text() for raw SQL to guarantee execution order and visibility
                        await db.execute(text("DELETE FROM finance_invoice_items WHERE invoice_id IN (SELECT id FROM finance_invoices WHERE document_id = :did)"), {"did": doc_id})
                        await db.execute(text("DELETE FROM finance_audit_flags WHERE invoice_id IN (SELECT id FROM finance_invoices WHERE document_id = :did)"), {"did": doc_id})
                        await db.execute(text("DELETE FROM finance_invoices WHERE document_id = :did"), {"did": doc_id})
                        await db.execute(text("DELETE FROM documents WHERE id = :did"), {"did": doc_id})
                        
                        await db.commit()
                        print(f"DEBUG: Force Overwrite Complete (Raw SQL)")
                except Exception as e:
                    print(f"DEBUG: DB Delete failed: {e}")
                    await db.rollback()
                    raise HTTPException(status_code=500, detail=f"Overwrite failed during DB cleanup: {str(e)}")
        
        # 1. Save locally
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        local_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Determine mime type
        mime_type = file.content_type or "application/pdf"
        
        try:
            # 3. Check for Custom API Key (BYOK)
            # In a real implementation we would query Tenant.gemini_api_key here
            # gemini_service.configure_for_tenant(...) 
            
            # Upload to Gemini
            gemini_file = await gemini_service.upload_file(
                file_path=local_path, 
                mime_type=mime_type, 
                display_name=file.filename
            )
            
            # 4. Create DB Entry
            new_doc = Document(
                filename=file.filename,
                tenant_id=tenant_id,
                file_uri=gemini_file.uri,
                status="indexing", # simple string now
                access_level="general" # Default
            )
            db.add(new_doc)
            await db.commit()
            await db.refresh(new_doc)
            
            return new_doc
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def chat_with_tenant(self, db: AsyncSession, tenant_id: int, user: User, query: str):
        """
        Retrieves docs accessible to User's Role and queries Gemini.
        """
        # 1. Get Accessible Documents
        # Logic: Get 'general' docs + docs matching user.role
        stmt = select(Document).where(
            Document.tenant_id == tenant_id,
            # (Document.access_level == "general") | (Document.access_level == user.role)
            # For MVP, let's just use all tenant docs
        )
        result = await db.execute(stmt)
        docs = result.scalars().all()
        
        if not docs:
            return "No documents found for this organization."

        file_uris = [doc.file_uri for doc in docs if doc.file_uri]
        
        # 2. Resolve Tenant Name for Context
        # We could load this from user.tenant, assuming eagers load or simple query
        company_name = "Your Company" 
        if user.tenant and user.tenant.company_name:
             company_name = user.tenant.company_name

        # 3. Call Gemini with Vertical Context
        answer = await gemini_service.generate_answer(
            query=query, 
            file_uris=file_uris,
            role=user.role,       # Pass User Role (Engineer, Hr, etc)
            company=company_name  # Pass Company Name
        )
        
        return answer

rag_service = RAGService()
