
# File: backend/app/seed_demo_data.py

import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.models import (
    Tenant, FinanceVendor, FinanceInvoice, FinanceInvoiceItem, 
    ChartOfAccounts, Employee, EmploymentContract, BankTransaction,
    Document, PayrollRun, VATReport, User, UserRole
)

# Setup Sync Engine for Seeding
import os
from dotenv import load_dotenv
load_dotenv()

# Use DATABASE_URL from env, but handle asyncpg prefix if present (convert to sync)
db_url = os.getenv("DATABASE_URL")
if db_url:
    if "postgresql+asyncpg" in db_url:
        db_url = db_url.replace("postgresql+asyncpg", "postgresql")
    elif "postgresql" in db_url and "psycopg2" not in db_url and "+" not in db_url:
        # standard postgresql:// might work, checking if we need explicit driver
        pass
else:
    # Fallback to SQLite if no env set
    db_url = "sqlite:///./corporate_memory.db"

print(f"DEBUG: Seeding to {db_url.split('@')[-1] if '@' in db_url else db_url}") # Safe print

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine)

# تأكد أن الجداول موجودة
# Base.metadata.drop_all(bind=engine) # REMOVED: Schema is verified correct
# Base.metadata.create_all(bind=engine) # REMOVED: Schema is verified correct

def seed_demo():
    db = SessionLocal()
    
    # 1. إنشاء شركة (Tenant) إذا لم توجد
    tenant = db.query(Tenant).filter_by(company_name="Finance Corp").first()
    if not tenant:
        tenant = Tenant(company_name="Finance Corp", subscription_status=True, subscribed_modules=["finance", "hr"])
        db.add(tenant)
        db.commit()
    
    print(f"Working with Tenant: {tenant.company_name} (ID: {tenant.id})")



    # 1.1 إنشاء وثائق (Documents)
    if db.query(Document).filter_by(tenant_id=tenant.id).count() == 0:
        doc1 = Document(tenant_id=tenant.id, filename="فاتورة_كهرباء_يناير.pdf", status="indexed", upload_date=datetime.now() - timedelta(days=10))
        doc2 = Document(tenant_id=tenant.id, filename="عقد_موظف_جديد.pdf", status="indexed", upload_date=datetime.now() - timedelta(days=2))
        db.add_all([doc1, doc2])
        db.commit()

    # 2. إنشاء الموردين (Vendors)
    vendors_data = [
        {"name": "مكتبة جرير", "tax_id": "300012345600003"},
        {"name": "شركة الكهرباء السعودية", "tax_id": "300098765400003"},
        {"name": "STC أعمال", "tax_id": "300055555500003"},
        {"name": "المقاولون العرب", "tax_id": "300011122200003"},
        {"name": "أمازون السعودية", "tax_id": "300099988800003"},
    ]
    
    vendors = []
    for v_data in vendors_data:
        vendor = db.query(FinanceVendor).filter_by(name=v_data["name"]).first()
        if not vendor:
            vendor = FinanceVendor(tenant_id=tenant.id, **v_data)
            db.add(vendor)
            db.commit()
        vendors.append(vendor)

    # 3. إنشاء دليل الحسابات (Chart of Accounts)
    coa_data = [
        {"code": "1000", "name": "Cash", "type": "Asset"},
        {"code": "1400", "name": "IT Equipment", "type": "Asset"},
        {"code": "5200", "name": "Maintenance", "type": "Expense"},
        {"code": "5300", "name": "Utilities", "type": "Expense"},
        {"code": "5400", "name": "Marketing", "type": "Expense"},
        {"code": "5500", "name": "Office Supplies", "type": "Expense"},
    ]
    
    for acc in coa_data:
        if not db.query(ChartOfAccounts).filter_by(code=acc["code"]).first():
            db.add(ChartOfAccounts(code=acc["code"], name=acc["name"], account_type=acc["type"]))
    db.commit()
    
    cash_acc = db.query(ChartOfAccounts).filter_by(code="1000").first()
    
    # 4. إنشاء فواتير عشوائية (Invoices) - خلال آخر 3 شهور
    categories = [
        {"desc": "لابتوب ماك بوك برو", "gl": "1400", "price": 8500, "type": "Asset"}, # أصول
        {"desc": "فاتورة كهرباء يناير", "gl": "5300", "price": 1200, "type": "Expense"}, # مصروفات
        {"desc": "اشتراك انترنت فايبر", "gl": "5300", "price": 400, "type": "Expense"},
        {"desc": "أدوات مكتبية وقرطاسية", "gl": "5500", "price": 250, "type": "Expense"},
        {"desc": "حملة تسويقية رمضان", "gl": "5400", "price": 5000, "type": "Expense"},
        {"desc": "صيانة مكيفات", "gl": "5200", "price": 600, "type": "Expense"},
    ]

    for _ in range(40): # إنشاء 40 فاتورة
        vendor = random.choice(vendors)
        cat = random.choice(categories)
        
        # تاريخ عشوائي
        days_ago = random.randint(0, 90)
        inv_date = datetime.now() - timedelta(days=days_ago)
        
        status = random.choice(["paid", "paid", "unpaid"]) # ترجيح المدفوع أكثر
        
        invoice = FinanceInvoice(
            tenant_id=tenant.id,
            document_id=None, # لا يوجد ملف فعلي
            vendor_id=vendor.id,
            invoice_number=f"INV-{random.randint(1000, 9999)}",
            invoice_date=inv_date,
            total_amount=cat["price"] * 1.15, # شامل الضريبة
            currency="SAR",
            payment_status=status,
            extraction_status="completed"
        )
        db.add(invoice)
        db.commit()
        
        # إضافة البند للفاتورة
        item = FinanceInvoiceItem(
            invoice_id=invoice.id,
            description=cat["desc"],
            quantity=1,
            unit_price=cat["price"],
            total_price=cat["price"],
            gl_code=cat["gl"],
            entry_type="Debit"
        )
        db.add(item)
        
        # 5. إذا كانت مدفوعة، أنشئ حركة بنكية (للمطابقة)
        if status == "paid":
            bank_tx = BankTransaction(
                tenant_id=tenant.id,
                date=inv_date + timedelta(days=1), # الدفع بعد الفاتورة بيوم
                description=f"POS Purchase - {vendor.name}",
                amount=-(cat["price"] * 1.15), # سحب (سالب)
                is_reconciled=True,
                matched_invoice_id=invoice.id
            )
            db.add(bank_tx)

    # 6. إنشاء موظفين (Employees) & Users
    # Create the Finance User for Login
    finance_user = db.query(User).filter_by(email="finance@company.com").first()
    if not finance_user:
        finance_user = User(
            email="finance@company.com",
            full_name="Fatima Finance",
            hashed_password="password",
            tenant_id=tenant.id,
            role=UserRole.ACCOUNTANT
        )
        db.add(finance_user)
        db.commit()

    if db.query(Employee).filter_by(tenant_id=tenant.id).count() == 0:
        emp1 = Employee(tenant_id=tenant.id, name="أحمد محمد", national_id="1010101010", email="ahmed@company.com")
        emp2 = Employee(tenant_id=tenant.id, name="سارة علي", national_id="1020202020", email="sara@company.com")
        db.add_all([emp1, emp2])
        db.commit()
        
        # عقود
        con1 = EmploymentContract(employee_id=emp1.id, basic_salary=6000, housing_allowance=1500, transport_allowance=500, start_date=datetime.now())
        con2 = EmploymentContract(employee_id=emp2.id, basic_salary=8000, housing_allowance=2000, transport_allowance=800, start_date=datetime.now())
        db.add_all([con1, con2])
        db.commit()

        # 7. مسير رواتب (Payroll Run)
        run = PayrollRun(tenant_id=tenant.id, month=datetime.now().month, year=2024, total_payout=17800, status="Paid")
        db.add(run)
        
        # 8. إقرار ضريبي (VAT Report)
        vat_report = VATReport(
            tenant_id=tenant.id, 
            period_start=datetime.strptime("2024-01-01", "%Y-%m-%d"), 
            period_end=datetime.strptime("2024-03-31", "%Y-%m-%d"), 
            total_sales=100000.0,
            total_sales_vat=15000.0,
            total_purchases=20000.0,
            total_purchases_vat=3000.0,
            net_vat_payable=12000.0, 
            status="Submitted"
        )
        db.add(vat_report)


    db.commit()
    db.close()
    print("✅ Database Seeded Successfully! The Dashboard is now ALIVE.")

if __name__ == "__main__":
    seed_demo()
