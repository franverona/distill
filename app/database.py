from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# TODO: Import settings from app.config and use settings.database_url
DATABASE_URL = "sqlite:///./distill.db"

# TODO: Create the SQLAlchemy engine
# Hint: for SQLite you need connect_args={"check_same_thread": False}
engine = None

# TODO: Create a SessionLocal factory using sessionmaker
# Hint: autocommit=False, autoflush=False, bind=engine
SessionLocal = None


class Base(DeclarativeBase):
    """Base class that all SQLAlchemy models will inherit from."""
    pass


def get_db():
    """
    FastAPI dependency that yields a database session and ensures it is
    closed after the request completes.

    Usage in a route:
        def my_route(db: Session = Depends(get_db)): ...
    """
    # TODO: Open a SessionLocal, yield it, and close it in a finally block
    pass
