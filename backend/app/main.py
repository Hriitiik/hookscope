from fastapi import FastAPI, Request

from app.config import get_settings

settings = get_settings()

is_dev = settings.env == "dev"

app = FastAPI(
    title="hookscope",
    docs_url="/docs" if is_dev else None,
    redoc_url=None,
    openapi_url="/openapi.json" if is_dev else None,
)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}
CSP = "default-src 'none'; frame-ancestors 'none'"


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items():
        response.headers[key] = value

    if not request.url.path.startswith(("/docs", "/openapi.json")):
        response.headers["Content-Security-Policy"] = CSP

    return response


@app.get("/health")
async def health():
    return {"status": "ok"}
