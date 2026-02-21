from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
