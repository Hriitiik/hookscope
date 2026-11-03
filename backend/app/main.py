from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

is_dev = settings.env == "dev"

app = FastAPI(
    title="hookscope",
    docs_url="/docs" if is_dev else None,
    redoc_url=None,
    openapi_url="/openapi.json" if is_dev else None,
)


@app.get("/health")
async def health():
    return {"status": "ok"}
