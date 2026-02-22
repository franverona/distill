from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


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

    model_config = ConfigDict(from_attributes=True)


class SummaryListResponse(BaseModel):
    """Response body for GET /history (paginated)."""

    items: list[SummaryResponse]
    total: int
    page: int
    size: int
