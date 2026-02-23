from sqlalchemy.orm import Session

from app.models.summary import Summary


def create(db: Session, url: str, summary: str, model: str) -> Summary:
    """
    Insert a new Summary record into the database and return it.
    """
    record = Summary(url=url, summary=summary, model=model)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_all(db: Session, page: int = 1, size: int = 10) -> dict:
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
    total = db.query(Summary).count()
    offset = (page - 1) * size
    items = (
        db.query(Summary)
        .order_by(Summary.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )
    return {"items": items, "total": total, "page": page, "size": size}


def get_by_id(db: Session, summary_id: int) -> Summary | None:
    """
    Fetch a single Summary by primary key.

    Returns:
        The Summary instance if found, otherwise None.
    """
    return db.get(Summary, summary_id)


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
