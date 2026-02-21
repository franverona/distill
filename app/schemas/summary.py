from datetime import datetime

from pydantic import BaseModel, HttpUrl


class SummarizeRequest(BaseModel):
    """Request body for POST /summarize."""

    # TODO: Add a `url` field of type HttpUrl
    # Pydantic will validate that the value is a well-formed URL for you


class SummaryResponse(BaseModel):
    """Response body returned after a successful summarization."""

    # TODO: Add fields that the client will receive:
    #   id, url, summary, model, created_at

    class Config:
        from_attributes = True  # allows creating this schema from an ORM model


class SummaryListResponse(BaseModel):
    """Response body for GET /history (paginated)."""

    # TODO: Add fields:
    #   items  : list[SummaryResponse]
    #   total  : int  — total number of records in the DB
    #   page   : int  — current page number
    #   size   : int  — page size
    pass
