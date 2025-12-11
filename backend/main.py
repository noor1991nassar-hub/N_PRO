from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import TenantMiddleware
from app.api.api import api_router

app = FastAPI(
    title="CorporateMemory API",
    description="Enterprise B2B SaaS Logic & RAG Platform (Arabic/RTL)",
    version="0.1.0",
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
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
