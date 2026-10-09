"""Cookies de session : httpOnly, path restreint, SameSite selon origine."""

from starlette.requests import Request
from starlette.responses import Response

from app.core.cookies import (
    ACCESS_COOKIE,
    REFRESH_COOKIE,
    clear_auth_cookies,
    set_auth_cookies,
)
from app.schemas.token import Token


def _request(origin: str | None = None, scheme: str = "http") -> Request:
    headers = [(b"host", b"localhost:8000")]
    if origin:
        headers.append((b"origin", origin.encode()))
    scope = {
        "type": "http",
        "scheme": scheme,
        "method": "POST",
        "path": "/api/v1/auth/login/json",
        "headers": headers,
        "query_string": b"",
    }
    return Request(scope)


def _token() -> Token:
    return Token(access_token="access-valeur", refresh_token="refresh-valeur")


def _cookies(response: Response) -> dict[str, str]:
    jar: dict[str, str] = {}
    for raw in response.headers.getlist("set-cookie"):
        name = raw.split("=", 1)[0]
        jar[name] = raw
    return jar


def test_cookies_are_httponly_and_not_readable_by_js():
    resp = Response()
    set_auth_cookies(resp, _request(), _token())
    jar = _cookies(resp)
    assert ACCESS_COOKIE in jar and REFRESH_COOKIE in jar
    assert "HttpOnly" in jar[ACCESS_COOKIE]
    assert "HttpOnly" in jar[REFRESH_COOKIE]
    assert "bestock_access=access-valeur" in jar[ACCESS_COOKIE]


def test_refresh_cookie_is_scoped_to_auth_routes():
    resp = Response()
    set_auth_cookies(resp, _request(), _token())
    jar = _cookies(resp)
    assert "Path=/api/v1/auth" in jar[REFRESH_COOKIE]
    assert "Path=/" in jar[ACCESS_COOKIE]


def test_same_site_origin_uses_lax():
    resp = Response()
    set_auth_cookies(resp, _request(origin="http://localhost:3000"), _token())
    jar = _cookies(resp)
    assert "SameSite=lax" in jar[ACCESS_COOKIE]
    assert "Secure" not in jar[ACCESS_COOKIE]


def test_cross_site_https_uses_none_and_secure():
    resp = Response()
    set_auth_cookies(
        resp,
        _request(origin="https://mon-app.vercel.app", scheme="https"),
        _token(),
    )
    jar = _cookies(resp)
    assert "SameSite=none" in jar[ACCESS_COOKIE]
    assert "Secure" in jar[ACCESS_COOKIE]


def test_clear_cookies_removes_both():
    resp = Response()
    request = _request()
    clear_auth_cookies(resp, request)
    jar = _cookies(resp)
    assert ACCESS_COOKIE in jar and REFRESH_COOKIE in jar
    assert "Max-Age=0" in jar[ACCESS_COOKIE]
