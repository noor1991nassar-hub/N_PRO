from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile, HTTPException
from app.models.document import Document, ProcessingStatus, FileType
from app.services.gemini import gemini_service
import shutil
import os
import uuid

# Temp storage for uploaded files before sending to Gemini
UPLOAD_DIR = "backend/temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class RAGService:
    async def upload_document(self, db: AsyncSession, file: UploadFile, workspace_id: int):
        """
        Orchestrates file upload:
        1. Save to local temp.
        2. Upload to Gemini.
        3. Save metadata to DB.
        """
        # 1. Save locally
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        local_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Determine mime type
        mime_type = file.content_type or "application/pdf"
        
        try:
            # 3. Upload to Gemini
            gemini_file = await gemini_service.upload_file(
                file_path=local_path, 
                mime_type=mime_type, 
                display_name=file.filename
            )
            
            # 4. Create DB Entry
            new_doc = Document(
                title=file.filename,
                file_type=FileType.PDF if "pdf" in mime_type else FileType.MP4, # Simplified logic
                local_path=local_path,
                gemini_file_uri=gemini_file.uri,
                status=ProcessingStatus.INDEXING,
                workspace_id=workspace_id
            )
            db.add(new_doc)
            await db.commit()
            await db.refresh(new_doc)
            
            return new_doc
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def chat_with_workspace(self, db: AsyncSession, workspace_id: int, query: str):
        """
        Retrieves all active docs for a workspace and queries Gemini.
        """
        # 1. Get all active documents for this workspace
        stmt = select(Document).where(
            Document.workspace_id == workspace_id,
            # Document.status == ProcessingStatus.ACTIVE # In real app, check active state
        )
        result = await db.execute(stmt)
        docs = result.scalars().all()
        
        if not docs:
            return "No documents found in this workspace."

        file_uris = [doc.gemini_file_uri for doc in docs if doc.gemini_file_uri]
        
        # 2. Call Gemini
        answer = await gemini_service.generate_answer(query=query, file_uris=file_uris)
        
        return answer

rag_service = RAGService()
