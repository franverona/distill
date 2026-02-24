import ipaddress
import socket
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator


class SummarizeRequest(BaseModel):
    """Request body for POST /summarize."""

    url: HttpUrl

    @field_validator("url")
    @classmethod
    def is_valid_url(cls, url: HttpUrl) -> HttpUrl:
        hostname = str(url.host)
        ip = socket.gethostbyname(hostname)
        ip_address = ipaddress.ip_address(ip)
        if ip_address.is_private or ip_address.is_loopback:
            raise ValueError("URL must point to a public address")
        return url


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
