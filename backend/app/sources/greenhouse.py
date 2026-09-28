"""Greenhouse adapter: fetch jobs from Greenhouse's public job board API.

API docs: https://developers.greenhouse.io/job-board.html
Endpoint:  GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
No API key is needed to read public job boards.
"""
import httpx

from app.models import Company, Job

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


def fetch_board(board_token: str, client: httpx.Client) -> list[dict]:
    """Return the raw job dicts for one company's Greenhouse board.

    Raises httpx.HTTPStatusError if Greenhouse answers with an error
    (for example 404 when the board token does not exist).
    """
    response = client.get(f"{BASE_URL}/{board_token}/jobs")
    response.raise_for_status()
    return response.json()["jobs"]


def parse_job(raw: dict, company: str) -> Job:
    """Turn one raw Greenhouse job dict into our normalized `Job`.

    Args:
        raw: one item from the "jobs" list Greenhouse returns
            (see tests/fixtures/greenhouse_jobs.json for a real example).
        company: our company name from companies.py (e.g. "Stripe"). We use
            it instead of raw["company_name"] so names match across sources.
    """
    # "location" can be missing or None, and so can its "name".
    location = (raw.get("location") or {}).get("name") or "Unknown"
    return Job(
        source="greenhouse",
        external_id=str(raw["id"]),
        company=company,
        title=raw["title"].strip(),
        location=location,
        url=raw["absolute_url"],
        posted_at=raw.get("first_published"),  # ISO string; Pydantic parses it
    )


def fetch_jobs(company: Company, client: httpx.Client) -> list[Job]:
    """Adapter entry point: all jobs for one Greenhouse company."""
    return [parse_job(raw, company.name) for raw in fetch_board(company.token, client)]
