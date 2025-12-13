from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_tenant_id
from app.services.finance_extractor import finance_extractor
from app.models.finance import FinanceInvoice, FinanceInvoiceItem
from app.models.tenant import Tenant
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter()

@router.post("/extract/{document_id}")
async def trigger_extraction(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    """
    Trigger AI Extraction for a Finance Document.
    Runs in background to avoid timeout.
    """
    # Verify Tenant Ownership (simplified)
    # In real app, check if document belongs to tenant
    
    print(f"--- TRIGGERING EXTRACTION FOR DOC ID: {document_id} ---")
    background_tasks.add_task(finance_extractor.process_document, db, document_id)
    return {"message": "Extraction started", "status": "processing"}

@router.get("/invoices")
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    """
    Get Data Grid (Tab 3) Data.
    """
    # Resolve Tenant ID
    target_name = tenant_name if tenant_name else "Construction Corp"
    stmt = select(Tenant).where(Tenant.company_name == target_name)
    result = await db.execute(stmt)
    tenant = result.scalars().first()
    
    if not tenant:
        # Lazy Seed if missing (Consistency with Upload)
        tenant = Tenant(
            company_name=target_name,
            subscription_status=True,
            subscribed_modules=["finance", "engineer"]
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)

    stmt = select(FinanceInvoice).where(FinanceInvoice.tenant_id == tenant.id).options(selectinload(FinanceInvoice.vendor))
    result = await db.execute(stmt)
    invoices = result.scalars().all()
    
    return invoices

@router.get("/invoice/{invoice_id}")
async def get_invoice_details(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    stmt = select(FinanceInvoice).where(FinanceInvoice.id == invoice_id).options(selectinload(FinanceInvoice.items), selectinload(FinanceInvoice.vendor))
    result = await db.execute(stmt)
    invoice = result.scalars().first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    return invoice
