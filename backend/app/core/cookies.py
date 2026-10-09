"""Cookies de session (access + refresh) en httpOnly, invisibles pour JS.

- access : path=/ (toutes les routes API)
- refresh : path restreint aux routes /auth (le cookie ne part que la ou il sert)
- SameSite=Lax en same-site (dev local, reverse proxy meme domaine) ;
  SameSite=None + Secure en cross-site (frontend/API sur des domaines
  differents, ex. Vercel + Railway) — la protection CSRF repose alors sur
  le preflight CORS (l'API n'accepte que application/json) + allow_origins.
"""

from urllib.parse import urlparse

from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.middleware.rate_limit import TRUST_PROXY

ACCESS_COOKIE = "bestock_access"
REFRESH_COOKIE = "bestock_refresh"


def _is_https(request: Request) -> bool:
    if request.url.scheme == "https":
        return True
    if TRUST_PROXY:
        return request.headers.get("x-forwarded-proto", "") == "https"
    return False


def _cross_site(request: Request) -> bool:
    """True si l'origine du navigateur n'est pas le domaine servi par l'API."""
    origin = request.headers.get("origin", "")
    if not origin or origin == "null":
        return False
    origin_host = (urlparse(origin).hostname or "").lower()
    host = (request.headers.get("host") or "").lower().split(":")[0]
    if not origin_host or not host:
        return False
    return origin_host != host


def _cookie_kwargs(request: Request) -> dict:
    secure = _is_https(request)
    # None impose Secure : en HTTP on reste en Lax (cross-site non supporte
    # en clair de toute facon)
    samesite = "none" if (secure and _cross_site(request)) else "lax"
    return {"httponly": True, "secure": secure, "samesite": samesite}


def set_auth_cookies(response: Response, request: Request, token) -> None:
    """Fixe les deux cookies a partir d'un schema Token."""
    kwargs = _cookie_kwargs(request)
    response.set_cookie(
        ACCESS_COOKIE,
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        **kwargs,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path=f"{settings.API_V1_STR}/auth",
        **kwargs,
    )


def clear_auth_cookies(response: Response, request: Request) -> None:
    kwargs = _cookie_kwargs(request)
    response.delete_cookie(ACCESS_COOKIE, path="/", **kwargs)
    response.delete_cookie(
        REFRESH_COOKIE, path=f"{settings.API_V1_STR}/auth", **kwargs
    )
