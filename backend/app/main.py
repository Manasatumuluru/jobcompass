"""Entry point for the JobCompass API.

Run from the backend folder with:
    uvicorn app.main:app --reload
"""
import time

import httpx
from fastapi import FastAPI

from app.aggregator import fetch_all_jobs
from app.companies import COMPANIES
from app.models import Job, SourceName

USER_AGENT = "JobCompass/0.1 (learning project)"
CACHE_SECONDS = 30 * 60  # refetch at most every 30 minutes

app = FastAPI(
    title="JobCompass",
    description="Finds 0-4 year roles at companies with H-1B sponsorship history.",
    version="0.1.0",
)

# Simple in-memory cache so we don't call ~30 external APIs on every request.
# It resets when the server restarts. Step 4 replaces it with a database.
_cache: dict = {"jobs": None, "fetched_at": 0.0}


def get_jobs() -> list[Job]:
    """Return cached jobs, fetching fresh ones if the cache is empty or old."""
    is_stale = time.monotonic() - _cache["fetched_at"] > CACHE_SECONDS
    if _cache["jobs"] is None or is_stale:
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=10.0) as client:
            _cache["jobs"] = fetch_all_jobs(COMPANIES, client)
        _cache["fetched_at"] = time.monotonic()
    return _cache["jobs"]


@app.get("/health")
def health_check() -> dict:
    """Simple check that the server is running. Deploy tools ping this."""
    return {"status": "ok"}


@app.get("/jobs")
def list_jobs(source: SourceName | None = None, company: str | None = None) -> list[Job]:
    """Returns jobs from Greenhouse, Lever, Ashby and Workday company boards.

    Optional filters: `source` (e.g. "lever") and `company` (e.g. "Spotify",
    not case sensitive). The first call takes ~20 seconds; later calls use
    the cache.
    """
    jobs = get_jobs()
    if source:
        jobs = [job for job in jobs if job.source == source]
    if company:
        jobs = [job for job in jobs if job.company.lower() == company.lower()]
    return jobs
