from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_tenant_id
from app.services.finance_extractor import finance_extractor
from app.models.finance import FinanceInvoice, FinanceInvoiceItem
from app.models.tenant import Tenant
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter()


# --- Helper: Tenant Resolution ---
async def resolve_tenant(db: AsyncSession, tenant_name: str) -> Tenant | None:
    target_name = tenant_name if tenant_name else "Finance Corp"
    stmt = select(Tenant).where(Tenant.company_name == target_name)
    result = await db.execute(stmt)
    tenant = result.scalars().first()
    
    if not tenant:
        # Lazy Seed if missing (special case for Finance Corp demo flow)
        if target_name == "Finance Corp":
             tenant = Tenant(
                company_name=target_name,
                subscription_status=True,
                subscribed_modules=["finance", "hr"]
            )
             db.add(tenant)
             await db.commit()
             await db.refresh(tenant)
    
    return tenant

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
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    print(f"--- TRIGGERING EXTRACTION FOR DOC ID: {document_id} ---")
    background_tasks.add_task(finance_extractor.process_document, document_id)
    return {"message": "Extraction started", "status": "processing"}

@router.get("/invoices")
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    """
    Get Data Grid (Tab 3) Data.
    """
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: return []

    stmt = select(FinanceInvoice).where(FinanceInvoice.tenant_id == tenant.id).options(
        selectinload(FinanceInvoice.vendor),
        selectinload(FinanceInvoice.items)
    )
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

# --- New Analytics & Reconciliation Endpoints ---
from app.services.analytics_service import analytics_service
from app.services.reconciliation_service import reconciliation_service

@router.get("/summary")
async def get_financial_summary(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: return {}

    return await analytics_service.get_financial_summary(db, tenant.id)

@router.get("/tasks")
async def get_accountant_tasks(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: return []

    return await analytics_service.get_accountant_tasks(db, tenant.id)

@router.post("/reconcile/run")
async def run_auto_reconciliation(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: raise HTTPException(status_code=404, detail="Tenant not found")
    
    return await reconciliation_service.auto_reconcile(db, tenant.id)

@router.post("/reconcile/seed")
async def seed_bank_transactions(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: raise HTTPException(status_code=404, detail="Tenant not found")
    
    return await reconciliation_service.create_dummy_bank_transactions(db, tenant.id)

# --- Tax (ZATCA) Endpoints ---
from app.services.tax_service import tax_service
from pydantic import BaseModel

class VATRequest(BaseModel):
    start_date: str
    end_date: str

@router.post("/tax/generate")
async def generate_tax_report(
    payload: VATRequest,
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: raise HTTPException(status_code=404, detail="Tenant not found")
    
    return await tax_service.generate_vat_report(db, tenant.id, payload.start_date, payload.end_date)

@router.get("/tax/history")
async def get_tax_history(
    db: AsyncSession = Depends(get_db),
    tenant_name: str = Depends(get_current_tenant_id),
):
    tenant = await resolve_tenant(db, tenant_name)
    if not tenant: return []

    return await tax_service.get_history(db, tenant.id)
