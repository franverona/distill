from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.logger import log
from app.repositories import summary as summary_repo
from app.schemas.summary import SummarizeRequest, SummaryListResponse, SummaryResponse
from app.services import ollama, scraper
from app.utils.pagination import build_pagination_links

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("/", response_model=SummaryResponse, status_code=201)
async def create_summary(request: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Accept a URL, scrape its content, generate a summary via Ollama, persist
    the result, and return it.
    """
    log.info("summary requested", url=str(request.url))
    text = await scraper.fetch_text(str(request.url))
    text = text[: settings.max_content_chars]
    summary = await ollama.summarize(text=text, length=request.length)
    record = summary_repo.create(
        db,
        url=str(request.url),
        content=text,
        summary=summary,
        model=settings.ollama_model,
    )
    log.info("summary created", id=record.id)
    return record


@router.get("/history", response_model=SummaryListResponse)
def list_summaries(
    page: int = 1,
    size: int = 10,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of all stored summaries.

    Query parameters:
        page — 1-based page number (default: 1)
        size — number of items per page (default: 10)
    """
    log.info("history requested", page=page, size=size, q=q)
    result = summary_repo.get_all(db, page=page, size=size, q=q)

    next_url, prev_url = build_pagination_links(
        base_path="/summarize/history",
        page=page,
        size=size,
        total=result["total"],
        extra_params={"q": q} if q else None,
    )

    return SummaryListResponse(
        items=[SummaryResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        next=next_url,
        prev=prev_url,
    )


@router.get("/history/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    Return a single summary by its ID.

    Raise HTTP 404 if no record with the given ID exists.
    """
    record = summary_repo.get_by_id(db, summary_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Not found")
    log.info("summary fetched", summary_id=summary_id)
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
    log.info("summary deleted", summary_id=summary_id)
    return Response(None, status_code=204)


@router.post(
    "/history/{summary_id}/retry", response_model=SummaryResponse, status_code=200
)
async def retry_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    Retry a single summary by its ID.

    Raise HTTP 404 if no record with the given ID exists.
    """
    log.info("retry requested", summary_id=summary_id)
    record = summary_repo.get_by_id(db, summary_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Not found")
    text = await scraper.fetch_text(record.url)
    text = text[: settings.max_content_chars]
    summary = await ollama.summarize(text=text)
    updated_record = summary_repo.update(
        db,
        record=record,
        content=text,
        summary=summary,
        model=record.model,
    )
    log.info("summary updated after retry", id=updated_record.id)
    return updated_record
