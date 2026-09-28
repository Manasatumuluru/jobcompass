"""Database setup: engine, sessions, and table creation.

Uses SQLite (a single file, jobcompass.db) for local development. Set the
DATABASE_URL environment variable to use PostgreSQL later, e.g.
postgresql+psycopg://user:password@host/dbname
"""
import os
from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./jobcompass.db")


class Base(DeclarativeBase):
    """Parent class for every table model (see db_models.py)."""


def make_engine(url: str) -> Engine:
    # SQLite only lets the thread that opened a connection use it. FastAPI
    # runs requests on several threads, so we turn that check off.
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = make_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db(bind: Engine = engine) -> None:
    """Create any tables that do not exist yet. Safe to run every startup."""
    from app import db_models  # noqa: F401  (importing registers the tables on Base)

    Base.metadata.create_all(bind)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one database session per request, always closed."""
    with SessionLocal() as session:
        yield session
