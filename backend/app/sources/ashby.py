"""Ashby adapter: fetch jobs from Ashby's public job posting API.

API docs: https://developers.ashbyhq.com/docs/public-job-posting-api
Endpoint:  GET https://api.ashbyhq.com/posting-api/job-board/{board_name}
No API key is needed.
"""
import httpx

from app.models import Company, Job

BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"


def fetch_board(board_name: str, client: httpx.Client) -> list[dict]:
    """Return the raw job dicts for one company's Ashby board."""
    response = client.get(f"{BASE_URL}/{board_name}")
    response.raise_for_status()
    return response.json()["jobs"]


def parse_job(raw: dict, company: str) -> Job:
    """Turn one raw Ashby job into our normalized `Job`."""
    return Job(
        source="ashby",
        external_id=raw["id"],
        company=company,
        title=raw["title"].strip(),  # some Ashby titles have stray spaces
        location=raw.get("location") or "Unknown",
        url=raw["jobUrl"],
        posted_at=raw.get("publishedAt"),
    )


def fetch_jobs(company: Company, client: httpx.Client) -> list[Job]:
    """Adapter entry point: all listed jobs for one Ashby company."""
    return [
        parse_job(raw, company.name)
        for raw in fetch_board(company.token, client)
        if raw.get("isListed", True)  # skip jobs hidden from the public board
    ]
