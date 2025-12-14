import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.document import Document
from app.services.finance_extractor import finance_extractor

async def manual_run():
    async with AsyncSessionLocal() as db:
        # Get last document
        stmt = select(Document).order_by(Document.id.desc()).limit(1)
        result = await db.execute(stmt)
        doc = result.scalars().first()
        
        if not doc:
            print("No documents found!")
            return

        print(f"--- TESTING EXTRACTION FOR DOC ID: {doc.id} (URI: {doc.file_uri}) ---")
        
    # Run extraction (it manages its own session now)
    try:
        invoice = await finance_extractor.process_document(doc.id)
        if invoice:
            print(f"SUCCESS! Invoice ID: {invoice.id}, Total: {invoice.total_amount}")
            print(f"Items: {len(invoice.items) if invoice.items else 0}")
        else:
            print("FAILURE: Extraction returned None.")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(manual_run())
