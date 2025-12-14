
# File: backend/app/seed_demo_data.py

import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.database import Base
from app.models import (
    Tenant, FinanceVendor, FinanceInvoice, FinanceInvoiceItem, 
    ChartOfAccounts, Employee, EmploymentContract, BankTransaction
)

# Setup Sync Engine for Seeding
db_uri = settings.SQLALCHEMY_DATABASE_URI
if "+aiosqlite" in db_uri:
    db_uri = db_uri.replace("+aiosqlite", "")
elif "+asyncpg" in db_uri:
    db_uri = db_uri.replace("+asyncpg", "")

engine = create_engine(db_uri)
SessionLocal = sessionmaker(bind=engine)

# تأكد أن الجداول موجودة
Base.metadata.create_all(bind=engine)

def seed_demo():
    db = SessionLocal()
    
    # 1. إنشاء شركة (Tenant) إذا لم توجد
    tenant = db.query(Tenant).filter_by(name="الشركة السعودية النموذجية").first()
    if not tenant:
        tenant = Tenant(name="الشركة السعودية النموذجية", plan="Enterprise")
        db.add(tenant)
        db.commit()
    
    print(f"Working with Tenant: {tenant.name} (ID: {tenant.id})")

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

    # 3. إنشاء دليل الحسابات (تأكد من وجوده)
    # (نعتمد على seed_coa.py السابق، لكن سنتأكد من وجود كود واحد على الأقل)
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

    # 6. إنشاء موظفين (Employees)
    if db.query(Employee).count() == 0:
        emp1 = Employee(tenant_id=tenant.id, name="أحمد محمد", national_id="1010101010", email="ahmed@company.com")
        emp2 = Employee(tenant_id=tenant.id, name="سارة علي", national_id="1020202020", email="sara@company.com")
        db.add_all([emp1, emp2])
        db.commit()
        
        # عقود
        con1 = EmploymentContract(employee_id=emp1.id, basic_salary=6000, housing_allowance=1500, transport_allowance=500, start_date=datetime.now())
        con2 = EmploymentContract(employee_id=emp2.id, basic_salary=8000, housing_allowance=2000, transport_allowance=800, start_date=datetime.now())
        db.add_all([con1, con2])

    db.commit()
    db.close()
    print("✅ Database Seeded Successfully! The Dashboard is now ALIVE.")

if __name__ == "__main__":
    seed_demo()
