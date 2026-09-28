"""Entry point for the JobCompass API.

Run from the backend folder with:
    uvicorn app.main:app --reload
"""
import httpx
from fastapi import FastAPI

from app.companies import GREENHOUSE_COMPANIES
from app.models import Job
from app.sources.greenhouse import fetch_greenhouse_jobs

USER_AGENT = "JobCompass/0.1 (learning project)"

app = FastAPI(
    title="JobCompass",
    description="Finds 0-4 year roles at companies with H-1B sponsorship history.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    """Simple check that the server is running. Deploy tools ping this."""
    return {"status": "ok"}


@app.get("/jobs")
def list_jobs() -> list[Job]:
    """Returns live jobs from each company's Greenhouse board.

    Fetches on every request for now (a few seconds). Step 4 stores jobs in a
    database so this becomes fast.
    """
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=10.0) as client:
        return fetch_greenhouse_jobs(GREENHOUSE_COMPANIES, client)
