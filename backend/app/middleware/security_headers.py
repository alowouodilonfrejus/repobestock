# ============================================
# BeStock - Security Headers Middleware
# Ajouter dans backend/app/middleware/security_headers.py
# ============================================
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import is_production

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Headers de securite
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # X-XSS-Protection obsolete, ne pas l'envoyer (deprecie depuis 2020)
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # HSTS uniquement si HTTPS (derriere proxy avec X-Forwarded-Proto)
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        if forwarded_proto == "https" or request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # CSP durcie : pas de unsafe-eval en prod.
        # La decision vient du serveur (ENV/drapeurs fournisseur) et non du
        # header Host, que n'importe quel client peut falsifier.
        is_dev = not is_production()
        script_src = "script-src 'self' 'unsafe-inline'"
        if is_dev:
            script_src += " 'unsafe-eval'"
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"{script_src}; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https: http://localhost:8000 http://localhost:3000; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        
        # Cookies sécurisés (si vous utilisez des cookies pour les tokens)
        # response.set_cookie(key="token", value="...", httponly=True, secure=True, samesite="lax")
        
        return response

def setup_security_headers(app):
    app.add_middleware(SecurityHeadersMiddleware)