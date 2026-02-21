from sqlalchemy.orm import Session

from app.models.summary import Summary


def create(db: Session, url: str, summary: str, model: str) -> Summary:
    """
    Insert a new Summary record into the database and return it.

    Steps:
        1. Instantiate a Summary model with the provided arguments
        2. Add it to the session: db.add(record)
        3. Commit the transaction: db.commit()
        4. Refresh the instance so DB-generated fields (id, created_at) are loaded:
           db.refresh(record)
        5. Return the record
    """
    # TODO: Implement the steps above
    pass


def get_all(db: Session, page: int = 1, size: int = 10) -> dict:
    """
    Return a paginated slice of all Summary records, ordered by most recent first.

    Steps:
        1. Query the total count of rows
        2. Calculate the offset: (page - 1) * size
        3. Query rows with .offset(offset).limit(size).all()
        4. Return a dict with keys: items, total, page, size

    Returns:
        {
            "items": list[Summary],
            "total": int,
            "page": int,
            "size": int,
        }
    """
    # TODO: Implement the steps above
    pass


def get_by_id(db: Session, summary_id: int) -> Summary | None:
    """
    Fetch a single Summary by primary key.

    Returns:
        The Summary instance if found, otherwise None.
    """
    # TODO: Use db.get(Summary, summary_id) or db.query(...).filter(...).first()
    pass
