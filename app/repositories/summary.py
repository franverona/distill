from datetime import datetime
from typing import TypedDict

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.summary import Summary
from app.schemas.summary import SummaryFormat, SummaryLength


class SummaryPage(TypedDict):
    items: list[Summary]
    total: int
    page: int
    size: int


def create(
    db: Session,
    url: str,
    content: str | None,
    summary: str,
    model: str,
    length: SummaryLength = "medium",
    format: SummaryFormat = "prose",
) -> Summary:
    """
    Insert a new Summary record into the database and return it.
    """
    record = Summary(
        url=url,
        content=content,
        summary=summary,
        model=model,
        length=length,
        format=format,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all(
    db: Session, page: int = 1, size: int = 10, q: str | None = None
) -> SummaryPage:
    """
    Return a paginated slice of all Summary records, ordered by most recent first.

    Returns:
        {
            "items": list[Summary],
            "total": int,
            "page": int,
            "size": int,
        }
    """
    query = db.query(Summary)
    if q:
        query = query.filter(
            or_(Summary.url.ilike(f"%{q}%"), Summary.summary.ilike(f"%{q}%"))
        )
    total = query.count()
    offset = (page - 1) * size
    items = query.order_by(Summary.created_at.desc()).offset(offset).limit(size).all()
    return {"items": items, "total": total, "page": page, "size": size}


def get_by_id(db: Session, summary_id: int) -> Summary | None:
    """
    Fetch a single Summary by primary key.

    Returns:
        The Summary instance if found, otherwise None.
    """
    return db.get(Summary, summary_id)


def get_by_url(db: Session, url: str, since: datetime | None = None) -> Summary | None:
    """
    Fetch a single Summary by url. If `since` is provided, only records
    created on or after since will be considered

    Returns:
        The Summary instance if found, otherwise None.
    """
    query = db.query(Summary).filter(Summary.url == url)
    if since:
        query = query.filter(Summary.created_at >= since)

    return query.order_by(Summary.created_at.desc()).first()


def delete(db: Session, summary_id: int) -> Summary | None:
    """
    Delete a Summary record by id.
    """
    record = db.get(Summary, summary_id)
    if record is None:
        return None

    db.delete(record)
    db.commit()
    return record


def update(
    db: Session,
    record: Summary,
    content: str,
    summary: str,
    length: SummaryLength,
    format: SummaryFormat,
    model: str,
) -> Summary:
    """
    Update a Summary record by id.
    """
    record.content = content
    record.summary = summary
    record.model = model
    record.length = length
    record.format = format
    db.commit()
    db.refresh(record)
    return record
