from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.middleware import TenantMiddleware
from app.api.api import api_router
from app.core.database import Base, engine
# Import models to ensure they are registered with Base
from app.models import tenant, document, finance

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="CorporateMemory API",
    description="Enterprise B2B SaaS Logic & RAG Platform (Arabic/RTL)",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "*"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TenantMiddleware)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "CorporateMemory API is running", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
