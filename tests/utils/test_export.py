import json
from unittest.mock import MagicMock

from app.utils.export import export_csv, export_jsonl


def make_record(
    id=1,
    url="https://example.com",
    summary="A summary",
    model="llama3.2",
    created_at="2026-01-01",
):
    r = MagicMock()
    r.id = id
    r.url = url
    r.summary = summary
    r.model = model
    r.created_at = created_at
    return r


async def read_response(response) -> bytes:
    chunks = []
    async for chunk in response.body_iterator:
        chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode())
    return b"".join(chunks)


async def test_export_csv_headers():
    response = export_csv([])
    content = await read_response(response)
    assert b"id,url,summary,model,created_at" in content


async def test_export_csv_contains_record():
    record = make_record(url="https://example.com", summary="A summary")
    response = export_csv([record])
    content = await read_response(response)
    assert b"example.com" in content
    assert b"A summary" in content


async def test_export_jsonl_contains_record():
    record = make_record(url="https://example.com", summary="A summary")
    response = export_jsonl([record])
    content = await read_response(response)
    data = json.loads(content.decode())
    assert data["url"] == "https://example.com"
    assert data["summary"] == "A summary"


async def test_export_csv_empty():
    response = export_csv([])
    content = await read_response(response)
    lines = content.decode().strip().split("\n")
    assert len(lines) == 1  # only header


async def test_export_jsonl_empty():
    response = export_jsonl([])
    content = await read_response(response)
    assert content == b""
