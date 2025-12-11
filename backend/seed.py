import asyncio
from app.core.database import AsyncSessionLocal
from app.models.tenant import Tenant, Workspace, User
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as db:
        # Check if tenant exists
        stmt = select(Tenant).where(Tenant.slug == "demo-tenant")
        result = await db.execute(stmt)
        tenant = result.scalars().first()

        if not tenant:
            print("Creating demo-tenant...")
            tenant = Tenant(name="Demo Inc.", slug="demo-tenant")
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
        else:
            print("Demo tenant already exists.")

        # Check if workspace exists
        stmt = select(Workspace).where(Workspace.tenant_id == tenant.id)
        result = await db.execute(stmt)
        workspace = result.scalars().first()

        if not workspace:
            print("Creating default workspace...")
            # For demo, we might need a dummy gemini_store_id or handle it in service
            workspace = Workspace(name="General", tenant_id=tenant.id, gemini_store_id="demo-store")
            db.add(workspace)
            await db.commit()
            print("Seeding complete.")
        else:
            print("Default workspace already exists.")

if __name__ == "__main__":
    asyncio.run(seed())
