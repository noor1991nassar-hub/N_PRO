import asyncio
from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant, User, UserRole
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as db:
        # Check if tenant exists (using company_name distinct enough for demo)
        # Note: 'slug' was removed in new schema, we use 'company_name'
        stmt = select(Tenant).where(Tenant.company_name == "Construction Corp")
        result = await db.execute(stmt)
        tenant = result.scalars().first()

        if not tenant:
            print("Creating Tenant: Construction Corp...")
            tenant = Tenant(
                company_name="Construction Corp",
                subscription_status=True,
                subscribed_modules=["engineer", "hr"]
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
        else:
            print("Tenant 'Construction Corp' already exists.")

        # Create Users for Verticals
        users_data = [
            {"email": "eng@demo.com", "name": "Ahmed Engineer", "role": UserRole.ENGINEER},
            {"email": "hr@demo.com", "name": "Sarah HR", "role": UserRole.HR},
            {"email": "admin@demo.com", "name": "Boss", "role": UserRole.ADMIN},
        ]

        for u in users_data:
            stmt = select(User).where(User.email == u["email"])
            result = await db.execute(stmt)
            existing_user = result.scalars().first()
            
            if not existing_user:
                print(f"Creating User: {u['name']} ({u['role']})...")
                user = User(
                    email=u["email"],
                    full_name=u["name"],
                    hashed_password="hashed_secret_password", # Dummy
                    tenant_id=tenant.id,
                    role=u["role"]
                )
                db.add(user)
        
        await db.commit()
        print("✅ Seeding Vertical SaaS Data Complete.")

if __name__ == "__main__":
    asyncio.run(seed())
