"""Database tables (SQLAlchemy ORM models).

These are separate from the Pydantic `Job` in models.py on purpose:
`Job` is the shape the API sends out, `JobRow` is how we store it, plus
bookkeeping columns (first_seen_at, last_seen_at, is_active).

All datetimes are stored as UTC without a timezone, because SQLite cannot
store timezones. repository.py converts on the way in and out.
"""
from datetime import datetime

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class JobRow(Base):
    __tablename__ = "jobs"
    # The same job id can only appear once per company and source.
    __table_args__ = (UniqueConstraint("source", "company", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(20))
    company: Mapped[str] = mapped_column(String(200), index=True)
    external_id: Mapped[str] = mapped_column(String(300))
    title: Mapped[str] = mapped_column(String(500))
    location: Mapped[str] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(2000))
    posted_at: Mapped[datetime | None]
    # False once the job disappears from the company's board.
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    first_seen_at: Mapped[datetime]
    last_seen_at: Mapped[datetime]
