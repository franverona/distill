from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.summary import SummarizeRequest, SummaryListResponse, SummaryResponse

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("/", response_model=SummaryResponse, status_code=201)
async def create_summary(request: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Accept a URL, scrape its content, generate a summary via Ollama, persist
    the result, and return it.

    Flow:
        1. Call scraper.fetch_text(request.url) to get the page text
        2. Call ollama.summarize(text) to get the LLM summary
        3. Call summary_repo.create(...) to persist it to the DB
        4. Return the saved record as a SummaryResponse
    """
    # TODO: Implement the steps described above
    pass


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
    # TODO: Call summary_repo.get_all(db, page, size) and return the result
    pass


@router.get("/history/{summary_id}", response_model=SummaryResponse)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    """
    Return a single summary by its ID.

    Raise HTTP 404 if no record with the given ID exists.
    """
    # TODO: Call summary_repo.get_by_id(db, summary_id)
    # TODO: If None, raise HTTPException(status_code=404, detail="Not found")
    pass
