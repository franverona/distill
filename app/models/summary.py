from app.database import Base


class Summary(Base):
    """
    SQLAlchemy model representing a stored URL summary.

    Columns to implement:
    - id          : integer primary key, auto-incremented
    - url         : the original URL that was summarised (string, not null)
    - content     : the raw scraped text (Text, nullable — store if you want)
    - summary     : the LLM-generated summary (Text, not null)
    - model       : the Ollama model used (string, not null)
    - created_at  : timestamp set automatically on insert
    """

    __tablename__ = "summaries"

    # TODO: Define each column using SQLAlchemy's Column(...) API
    # Example:
    #   id = Column(Integer, primary_key=True, index=True)
