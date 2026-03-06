import ipaddress
import socket
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator

from app.config import settings

SummaryLength = Literal["short", "medium", "long"]

SummaryFormat = Literal["prose", "markdown"]


class SummarizeRequest(BaseModel):
    """Request body for POST /summarize."""

    url: HttpUrl
    length: SummaryLength = "medium"
    format: SummaryFormat = "prose"

    @field_validator("url")
    @classmethod
    def no_private_or_blocked_urls(cls, v: HttpUrl) -> HttpUrl:
        host = v.host or ""

        ip = socket.gethostbyname(host)
        if ipaddress.ip_address(ip).is_private or ipaddress.ip_address(ip).is_loopback:
            raise ValueError("URL must point to a public address")

        # Blocklist check
        if any(host == d or host.endswith(f".{d}") for d in settings.blocked_domains):
            raise ValueError("URL domain is blocked")

        # Allowlist check (if configured)
        if settings.allowed_domains:
            if not any(
                host == d or host.endswith(f".{d}") for d in settings.allowed_domains
            ):
                raise ValueError("URL domain is not in the allowlist")

        return v


class SummaryResponse(BaseModel):
    """Response body returned after a successful summarization."""

    id: int
    url: str
    summary: str
    model: str
    reading_time_minutes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SummaryListResponse(BaseModel):
    """Response body for GET /history (paginated)."""

    items: list[SummaryResponse]
    total: int
    page: int
    size: int
    next: str | None = None
    prev: str | None = None


class BatchSummarizeRequest(BaseModel):
    urls: list[HttpUrl]
    length: SummaryLength = "medium"
    format: SummaryFormat = "prose"

    @field_validator("urls")
    @classmethod
    def limit_batch_size(cls, v):
        if len(v) > 10:
            raise ValueError("Batch size cannot exceed 10 URLs")
        return v


class BatchResultItem(BaseModel):
    url: str
    success: bool
    result: SummaryResponse | None = None
    error: str | None = None


class BatchSummarizeResponse(BaseModel):
    results: list[BatchResultItem]
