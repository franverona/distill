from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base
from app.schemas.summary import SummaryFormat, SummaryLength


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    length: Mapped[SummaryLength] = mapped_column(
        String, nullable=False, server_default="medium"
    )
    format: Mapped[SummaryFormat] = mapped_column(
        String, nullable=False, server_default="prose"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def reading_time_minutes(self) -> int:
        if not self.content:
            return 0
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))  # average 200 wpm
