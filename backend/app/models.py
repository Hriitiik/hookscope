from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class Endpoint(Base):
    __tablename__ = "endpoints"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class CapturedRequest(Base):
    __tablename__ = "captured_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("endpoints.id", ondelete="CASCADE"), index=True
    )
    method: Mapped[str] = mapped_column(String(16))
    query_string: Mapped[str] = mapped_column(String(2048), default="")
    headers: Mapped[list[list[str]]] = mapped_column(JSON)
    body: Mapped[bytes] = mapped_column(LargeBinary)
    source_ip: Mapped[str] = mapped_column(String(45))
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
