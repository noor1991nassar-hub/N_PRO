from fastapi import APIRouter
from app.api.endpoints import documents, chat, finance

api_router = APIRouter()
api_router.include_router(documents.router, prefix="/app", tags=["documents"])
api_router.include_router(chat.router, prefix="/app", tags=["chat"])
api_router.include_router(finance.router, prefix="/app/finance", tags=["finance"])
