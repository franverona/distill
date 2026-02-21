from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SummarizeRequest(BaseModel):
    """Request body for POST /summarize."""

    url: HttpUrl


class SummaryResponse(BaseModel):
    """Response body returned after a successful summarization."""

    id: int
    url: str
    summary: str
    model: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this schema from an ORM model


class SummaryListResponse(BaseModel):
    """Response body for GET /history (paginated)."""

    items: list[SummaryResponse]
    total: int
    page: int
    size: int
