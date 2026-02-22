from typing import cast

from app.repositories import summary as summary_repo


def test_create(db_session):
    record = summary_repo.create(
        db_session, url="https://example.com", summary="A summary", model="llama3.2"
    )

    assert record.id is not None
    assert str(record.url) == "https://example.com"
    assert str(record.summary) == "A summary"
    assert str(record.model) == "llama3.2"
    assert record.created_at is not None


def test_get_by_id(db_session):
    record_create = summary_repo.create(
        db_session, url="https://example.com", summary="A summary", model="llama3.2"
    )
    record = summary_repo.get_by_id(db_session, cast(int, record_create.id))

    assert record is not None
    assert str(record.url) == "https://example.com"
    assert str(record.summary) == "A summary"
    assert str(record.model) == "llama3.2"
    assert record.created_at is not None


def test_get_by_id_not_found(db_session):
    record = summary_repo.get_by_id(db_session, 9999)

    assert record is None


def test_get_all_pagination(db_session):
    summary_repo.create(
        db_session,
        url="https://example-1.com",
        summary="A summary #1",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example-2.com",
        summary="A summary #2",
        model="llama3.2",
    )
    summary_repo.create(
        db_session,
        url="https://example-3.com",
        summary="A summary #3",
        model="llama3.2",
    )
    items = summary_repo.get_all(db_session, page=1, size=2)

    assert len(items["items"]) == 2
    assert items["total"] == 3
    assert items["page"] == 1
    assert items["size"] == 2


def test_get_all_empty(db_session):
    items = summary_repo.get_all(db_session, page=1, size=2)

    assert len(items["items"]) == 0
    assert items["total"] == 0
    assert items["page"] == 1
    assert items["size"] == 2
