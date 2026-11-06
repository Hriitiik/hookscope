from sqlalchemy import select

from app.models import CapturedRequest


async def make_token(client) -> str:
    response = await client.post("/endpoints")
    assert response.status_code == 201
    return response.json()["token"]


async def test_unknown_token_returns_404(client):
    response = await client.post("/hooks/does-not-exist", content=b"x")
    assert response.status_code == 404


async def test_capture_stores_request(client, maker):
    token = await make_token(client)
    response = await client.post(
        f"/hooks/{token}?src=test",
        json={"event": "payment.completed"},
        headers={"X-Custom": "abc"},
    )
    assert response.status_code == 200

    async with maker() as session:
        row = await session.scalar(select(CapturedRequest))
    assert row.method == "POST"
    assert row.query_string == "src=test"
    assert b"payment.completed" in row.body
    assert ["x-custom", "abc"] in row.headers


async def test_binary_body_stored_intact(client, maker):
    token = await make_token(client)
    payload = bytes(range(256))  # not valid UTF-8
    await client.post(f"/hooks/{token}", content=payload)

    async with maker() as session:
        row = await session.scalar(select(CapturedRequest))
    assert row.body == payload


async def test_duplicate_headers_preserved(client, maker):
    token = await make_token(client)
    await client.get(f"/hooks/{token}", headers=[("x-dup", "1"), ("x-dup", "2")])

    async with maker() as session:
        row = await session.scalar(select(CapturedRequest))
    dup_values = [v for k, v in row.headers if k == "x-dup"]
    assert dup_values == ["1", "2"]


async def test_oversized_body_rejected(client, maker):
    token = await make_token(client)
    response = await client.post(f"/hooks/{token}", content=b"a" * (1_048_576 + 1))
    assert response.status_code == 413

    async with maker() as session:
        assert await session.scalar(select(CapturedRequest)) is None
