from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            # In a real app, strict validation would happen here
            request.state.tenant_id = tenant_id
        
        response = await call_next(request)
        return response
