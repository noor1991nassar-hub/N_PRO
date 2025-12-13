import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.document import Document
from app.models.finance import FinanceInvoice, FinanceInvoiceItem, FinanceVendor
from app.services.gemini import gemini_service
from app.schemas.finance import InvoiceExtract
import logging

logger = logging.getLogger(__name__)

class FinanceExtractorService:
    async def process_document(self, db: AsyncSession, document_id: int):
        """
        Orchestrates the extraction process:
        1. Get Document URI.
        2. Call AI for JSON extraction (Arabic Context).
        3. Parse & Save to DB.
        """
        try:
            # 1. Fetch Document
            stmt = select(Document).where(Document.id == document_id)
            result = await db.execute(stmt)
            document = result.scalars().first()
            
            if not document or not document.file_uri:
                raise ValueError("Document not found or not indexed in Gemini.")

            # 2. Call AI (Arabic Prompt)
            prompt = """
            أنت محاسب خبير ومدخل بيانات دقيق. 
            المهمة: استخرج البيانات من صورة/ملف الفاتورة المرفق بدقة 100%.
            
            ركز بشكل خاص على "جدول البنود" (Line Items Table). يجب استخراج **جميع الصفوف** الموجودة في الجدول.
            انتبه: الجدول قد يكون باللغة العربية (من اليمين لليسار). الأعمدة عادة تشمل: الصنف/البيان، الكمية، السعر الافرادي، الإجمالي.
            
            المطلوب منك إخراج البيانات بصيغة JSON فقط تتبع هذا الهيكل:
            {
                "vendor_name": "string",
                "vendor_tax_id": "string",
                "invoice_number": "string",
                "invoice_date": "YYYY-MM-DD",
                "total_amount": float,
                "currency": "SAR",
                "items": [
                    {
                        "description": "string",
                        "quantity": float,
                        "unit_price": float,
                        "total_price": float,
                        "category": "string (مهم: حاول تصنيف البند، مثال: 'صيانة', 'أثاث', 'تسويق', 'زهور')"
                    }
                ]
            }
            
            ملاحظات هامة:
            - إذا كان التاريخ هجرياً حوله لميلادي.
            - تأكد من دقة الأرقام في البنود.
            - لا تترك قائمة "items" فارغة إذا كان هناك جدول في الصورة.
            """
            
            response_text = await gemini_service.generate_answer(
                query=prompt,
                file_uris=[document.file_uri],
                role="accountant",
                company="Unknown",
                system_instruction="You are a JSON-only extraction engine. Output ONLY raw JSON."
            )
            
            # 3. Clean & Parse JSON
            cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
            # Handle potential leading/trailing garbage (e.g. "Here is the JSON: { ... }")
            if "{" in cleaned_text:
                cleaned_text = cleaned_text[cleaned_text.find("{"):cleaned_text.rfind("}")+1]
            
            try:
                data_dict = json.loads(cleaned_text)
                logger.info(f"AI Extraction Success. Items count: {len(data_dict.get('items', []))}")
                print(f"DEBUG: Extracted {len(data_dict.get('items', []))} items: {data_dict.get('items')}")
            except json.JSONDecodeError:
                logger.error(f"JSON Parsing Failed. Raw: {response_text}")
                # Fallback failure - requires prompt tuning if frequent
                raise ValueError("AI response was not valid JSON")

            # Use Pydantic for validation
            extracted_data = InvoiceExtract(**data_dict)

            # 4. Save to DB (Relational)
            
            # A. Vendor (Upsert)
            stmt = select(FinanceVendor).where(FinanceVendor.name == extracted_data.vendor_name, FinanceVendor.tenant_id == document.tenant_id)
            result = await db.execute(stmt)
            vendor = result.scalars().first()
            
            if not vendor:
                vendor = FinanceVendor(
                    name=extracted_data.vendor_name,
                    tax_id=extracted_data.vendor_tax_id,
                    tenant_id=document.tenant_id
                )
                db.add(vendor)
                await db.flush()
                await db.refresh(vendor)
                
            # B. Invoice Header
            stmt = select(FinanceInvoice).where(FinanceInvoice.document_id == document_id).options(selectinload(FinanceInvoice.items))
            result = await db.execute(stmt)
            existing_invoice = result.scalars().first()
            
            if existing_invoice:
                 # Update existing
                 existing_invoice.total_amount = extracted_data.total_amount
                 existing_invoice.invoice_number = extracted_data.invoice_number
                 existing_invoice.invoice_date = extracted_data.invoice_date
                 existing_invoice.currency = extracted_data.currency
                 existing_invoice.vendor_id = vendor.id
                 existing_invoice.extraction_status = "completed"
                 
                 # Clear old items to replace (SQLAlchemy delete-orphan will handle deletion)
                 existing_invoice.items = []
                 invoice = existing_invoice
            else:
                from datetime import datetime
                # Parse Date if possible (Simple try/except)
                inv_date = None
                if extracted_data.invoice_date:
                    try:
                        inv_date = datetime.strptime(extracted_data.invoice_date, "%Y-%m-%d")
                    except:
                        pass

                invoice = FinanceInvoice(
                    tenant_id=document.tenant_id,
                    document_id=document.id,
                    vendor_id=vendor.id,
                    invoice_number=extracted_data.invoice_number,
                    invoice_date=inv_date,
                    total_amount=extracted_data.total_amount,
                    currency=extracted_data.currency,
                    extraction_status="completed"
                )
                db.add(invoice)
                await db.flush()
            
            # C. Line Items
            # If we updated existing_invoice, .items is now empty list. We just append.
            # If new invoice, .items is empty collection.
            
            for item in extracted_data.items:
                # Direct object creation is safer than appending to list if session is tricky
                # But appending to relation is more idiomatic
                db_item = FinanceInvoiceItem(
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    category=item.category
                )
                invoice.items.append(db_item)
                
            await db.commit()
            return invoice
            
        except Exception as e:
            logger.error(f"Extraction Failed: {e}")
            import traceback
            traceback.print_exc()
            return None

finance_extractor = FinanceExtractorService()
