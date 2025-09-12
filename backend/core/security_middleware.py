# ADICIONAR em backend/core/security_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import hashlib
import time

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware de segurança avançada"""
    
    async def dispatch(self, request: Request, call_next):
        # 1. Content Security Policy
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 2. Request ID para rastreamento
        request_id = hashlib.md5(f"{time.time()}{request.url}".encode()).hexdigest()[:8]
        response.headers["X-Request-ID"] = request_id
        
        # 3. Remover headers sensíveis
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        
        return response