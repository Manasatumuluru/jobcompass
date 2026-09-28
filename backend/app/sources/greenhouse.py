"""Fetch jobs from Greenhouse's public job board API.

API docs: https://developers.greenhouse.io/job-board.html
Endpoint:  GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
No API key is needed to read public job boards.
"""
import logging
import time

import httpx

from app.models import Job

logger = logging.getLogger(__name__)

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"
DELAY_SECONDS = 0.5  # be polite: small pause between companies


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
        title=raw["title"],
        location=location,
        url=raw["absolute_url"],
        updated_at=raw["updated_at"],  # Pydantic parses the ISO string into a datetime
    )


def fetch_greenhouse_jobs(companies: list[dict[str, str]], client: httpx.Client) -> list[Job]:
    """Fetch and normalize jobs for every company in the list.

    If one company fails (bad token, network error), log it and keep going,
    so one broken board does not hide jobs from the others.
    """
    jobs: list[Job] = []
    for i, company in enumerate(companies):
        if i > 0:
            time.sleep(DELAY_SECONDS)
        try:
            raw_jobs = fetch_board(company["board_token"], client)
        except httpx.HTTPError as exc:
            logger.warning("Skipping %s: %s", company["name"], exc)
            continue
        jobs.extend(parse_job(raw, company["name"]) for raw in raw_jobs)
    return jobs
