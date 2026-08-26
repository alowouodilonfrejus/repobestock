# ============================================
# BeStock - Rate Limiting (pur Starlette, zéro dépendance)
# Sliding window en mémoire, par IP, sur les routes sensibles
# ============================================
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Fenêtre glissante : max N requêtes par fenêtre et par IP
RULES = {
    ("/login", "/register", "/inscription"): (5, 60),      # 5 req / minute — inclut /employes/inscription
    ("/refresh", "/logout"): (10, 60),     # 10 req / minute
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[tuple, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/")
        # X-Forwarded-For derriere proxy (sinon NAT/proxy = 127.0.0.1 -> bypass)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "?"
        method = request.method

        for paths, (limit, window) in RULES.items():
            if any(p in path for p in paths) and method == "POST":
                key = (client_ip, path)
                now = time.monotonic()
                hits = self._hits[key]
                while hits and now - hits[0] > window:
                    hits.popleft()
                if len(hits) >= limit:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Trop de requêtes, réessayez plus tard"},
                        headers={"Retry-After": str(window)},
                    )
                hits.append(now)
                break

        return await call_next(request)


def setup_rate_limiting(app) -> None:
    app.add_middleware(RateLimitMiddleware)
