from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.finance import FinanceInvoice, FinanceInvoiceItem, VATReport

class TaxService:
    async def generate_vat_report(self, db: AsyncSession, tenant_id: int, start_date: str, end_date: str):
        """
        Generates a VAT Return Report for the given period.
        Assumes standard 15% VAT rate.
        """
        # 1. Calculate Total Sales (Output Tax Context)
        # Invoices where GL Code starts with '4' (Revenue)
        stmt_sales = select(func.sum(FinanceInvoiceItem.total_price)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoice.invoice_date >= start_date,
            FinanceInvoice.invoice_date <= end_date,
            FinanceInvoiceItem.gl_code.like("4%")
        )
        sales_result = await db.execute(stmt_sales)
        total_sales = sales_result.scalar() or 0.0
        output_vat = total_sales * 0.15

        # 2. Calculate Total Purchases (Input Tax Context)
        # Invoices where GL Code starts with '5' (Expenses) or '1' (Assets)
        stmt_purchases = select(func.sum(FinanceInvoiceItem.total_price)).join(FinanceInvoice).where(
            FinanceInvoice.tenant_id == tenant_id,
            FinanceInvoice.invoice_date >= start_date,
            FinanceInvoice.invoice_date <= end_date,
            (FinanceInvoiceItem.gl_code.like("5%") | FinanceInvoiceItem.gl_code.like("1%"))
        )
        purchases_result = await db.execute(stmt_purchases)
        total_purchases = purchases_result.scalar() or 0.0
        input_vat = total_purchases * 0.15

        # 3. Net Payable
        net_payable = output_vat - input_vat

        # 4. Create Report Record
        report = VATReport(
            tenant_id=tenant_id,
            period_start=start_date,
            period_end=end_date,
            total_sales=total_sales,
            total_sales_vat=output_vat,
            total_purchases=total_purchases,
            total_purchases_vat=input_vat,
            net_vat_payable=net_payable,
            status="Draft"
        )
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return report

    async def get_history(self, db: AsyncSession, tenant_id: int):
        stmt = select(VATReport).where(VATReport.tenant_id == tenant_id).order_by(VATReport.generated_at.desc())
        result = await db.execute(stmt)
        return result.scalars().all()

tax_service = TaxService()
