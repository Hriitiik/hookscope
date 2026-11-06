import secrets
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Endpoint

router = APIRouter(prefix="/endpoints", tags=["endpoints"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", status_code=201)
async def create_endpoint(session: SessionDep) -> dict[str, str]:
    endpoint = Endpoint(token=secrets.token_urlsafe(16))  # 128 bits of randomness
    session.add(endpoint)
    await session.commit()
    return {"token": endpoint.token, "path": f"/hooks/{endpoint.token}"}
