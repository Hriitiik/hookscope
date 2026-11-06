from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app import models  # noqa: F401
from app.config import get_settings
from app.db import Base, get_engine
from app.endpoints import router as endpoints_router
from app.hooks import router as hooks_router

settings = get_settings()

is_dev = settings.env == "dev"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="hookscope",
    lifespan=lifespan,
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


app.include_router(endpoints_router)
app.include_router(hooks_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
