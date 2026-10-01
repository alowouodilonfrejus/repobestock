# ============================================
# BeStock - Rate Limiting (pur Starlette, zero dependance)
# Sliding window partage entre workers (fichier + flock),
# par IP, sur les routes sensibles
# ============================================
import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

try:
    import fcntl

    _HAS_FCNTL = True
except ImportError:  # Windows sans WSL : repli memoire locale
    _HAS_FCNTL = False

# Fenetre glissante : max N requetes par fenetre et par IP
RULES = {
    ("/login", "/register", "/inscription"): (5, 60),      # 5 req / minute — inclut /employes/inscription
    ("/refresh", "/logout"): (10, 60),     # 10 req / minute
}

TRUST_PROXY = os.getenv("TRUST_PROXY", "false").strip().lower() in {"1", "true", "yes"}
STORE_PATH = Path(os.getenv("RATE_LIMIT_STORE", "/tmp/bestock_ratelimit.json"))


def client_ip(request: Request) -> str:
    """IP du client. X-Forwarded-For n'est pris en compte que si TRUST_PROXY
    est active : sinon n'importe quel client peut falsifier son IP."""
    if TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "?"


class _MemoryStore:
    """Repli sans fichier : memoire locale au process (un worker = un compteur)."""

    def __init__(self) -> None:
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str, window: int, limit: int) -> bool:
        now = time.time()
        hits = self._hits[key]
        while hits and now - hits[0] > window:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


class _FileStore:
    """Magasin partage entre workers : lecture/ecriture atomique sous flock."""

    def allow(self, key: str, window: int, limit: int) -> bool:
        now = time.time()
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STORE_PATH, "a+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                raw = f.read()
                data = json.loads(raw) if raw.strip() else {}

                # Purge globale des cles inactives depuis trop longtemps
                for k in list(data):
                    if now - max(data[k], default=0) > 3600:
                        del data[k]

                # Fenetre glissante de la cle concernee (sa regle define sa fenetre)
                hits = [t for t in data.get(key, []) if now - t <= window]
                if len(hits) >= limit:
                    data[key] = hits
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f)
                    return False
                hits.append(now)
                data[key] = hits

                f.seek(0)
                f.truncate()
                json.dump(data, f)
                return True
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)


_store: _MemoryStore | _FileStore = _FileStore() if _HAS_FCNTL else _MemoryStore()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path.rstrip("/")
        ip = client_ip(request)
        method = request.method

        for paths, (limit, window) in RULES.items():
            if any(p in path for p in paths) and method == "POST":
                key = f"{ip}|{path}"
                try:
                    allowed = _store.allow(key, window, limit)
                except OSError:
                    # Magasin inaccessible : on ne bloque pas la requete
                    allowed = True
                if not allowed:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Trop de requetes, reessayez plus tard"},
                        headers={"Retry-After": str(window)},
                    )
                break

        return await call_next(request)


def setup_rate_limiting(app) -> None:
    app.add_middleware(RateLimitMiddleware)
