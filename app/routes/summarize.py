from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.repositories import summary as summary_repo
from app.schemas.summary import SummarizeRequest, SummaryListResponse, SummaryResponse
from app.services import ollama, scraper

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("/", response_model=SummaryResponse, status_code=201)
async def create_summary(request: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Accept a URL, scrape its content, generate a summary via Ollama, persist
    the result, and return it.
    """
    text = await scraper.fetch_text(str(request.url))
    summary = await ollama.summarize(text)
    record = summary_repo.create(
        db,
        url=str(request.url),
        summary=summary,
        model=settings.ollama_model,
    )
    return record


@router.get("/history", response_model=SummaryListResponse)
def list_summaries(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of all stored summaries.

    Query parameters:
        page — 1-based page number (default: 1)
        size — number of items per page (default: 10)
    """
    return summary_repo.get_all(db, page=page, size=size)


@router.get("/history/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    Return a single summary by its ID.

    Raise HTTP 404 if no record with the given ID exists.
    """
    record = summary_repo.get_by_id(db, summary_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Not found")
    return record


@router.delete("/history/{summary_id}", status_code=204)
def delete_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    Delete a single summary by its ID.

    Raise HTTP 404 if no record with the given ID exists.
    Return HTTP 204 if record was successfully deleted.
    """
    record = summary_repo.delete(db, summary_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Not found")
    return Response(None, status_code=204)
