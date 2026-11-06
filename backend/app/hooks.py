from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db import get_session
from app.models import CapturedRequest, Endpoint

router = APIRouter(tags=["hooks"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]

METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]


async def read_limited_body(request: Request, limit: int) -> bytes:
    declared = request.headers.get("content-length")
    if declared is not None and declared.isdigit() and int(declared) > limit:
        raise HTTPException(status_code=413, detail="Payload too large")

    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            raise HTTPException(status_code=413, detail="Payload too large")
        chunks.append(chunk)
    return b"".join(chunks)


@router.api_route("/hooks/{token}", methods=METHODS)
async def capture(token: str, request: Request, session: SessionDep) -> dict[str, int | str]:
    endpoint = await session.scalar(select(Endpoint).where(Endpoint.token == token))
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Not found")

    body = await read_limited_body(request, get_settings().max_body_bytes)

    captured = CapturedRequest(
        endpoint_id=endpoint.id,
        method=request.method,
        query_string=request.url.query[:2048],
        headers=[[k.decode("latin-1"), v.decode("latin-1")] for k, v in request.headers.raw],
        body=body,
        source_ip=request.client.host if request.client else "unknown",
    )
    session.add(captured)
    await session.commit()
    return {"status": "captured", "id": captured.id}
