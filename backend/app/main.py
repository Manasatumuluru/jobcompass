"""Entry point for the JobCompass API.

Run from the backend folder with:
    uvicorn app.main:app --reload
Load jobs first with `python -m app.refresh` (or POST /refresh).
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.companies import COMPANIES
from app.db import get_session, init_db
from app.dedupe import dedupe_jobs
from app.models import Job, SourceName
from app.refresh import CompanyRefresh, make_http_client, refresh_jobs
from app.repository import list_active_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()  # create tables on startup if they don't exist
    yield


app = FastAPI(
    title="JobCompass",
    description="Finds 0-4 year roles at companies with H-1B sponsorship history.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health_check() -> dict:
    """Simple check that the server is running. Deploy tools ping this."""
    return {"status": "ok"}


@app.get("/jobs")
def list_jobs(
    source: SourceName | None = None,
    company: str | None = None,
    session: Session = Depends(get_session),
) -> list[Job]:
    """Active jobs from the database, duplicates removed, newest first.

    Optional filters: `source` (e.g. "lever") and `company` (e.g. "Spotify",
    not case sensitive). Empty until the first refresh.
    """
    return dedupe_jobs(list_active_jobs(session, source, company))


@app.post("/refresh")
def refresh(session: Session = Depends(get_session)) -> list[CompanyRefresh]:
    """Fetch every company's board now and save to the database (~25 seconds)."""
    with make_http_client() as client:
        return refresh_jobs(session, COMPANIES, client)
