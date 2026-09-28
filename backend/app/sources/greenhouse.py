"""Greenhouse adapter: fetch jobs from Greenhouse's public job board API.

API docs: https://developers.greenhouse.io/job-board.html
Endpoint:  GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
No API key is needed to read public job boards.
"""
import httpx

from app.models import Company, Job
from app.sources.base import JobSource

BASE_URL = "https://boards-api.greenhouse.io/v1/boards"


class GreenhouseSource(JobSource):
    name = "greenhouse"

    def fetch_raw(self, company: Company, client: httpx.Client) -> list[dict]:
        """Return the raw job dicts for one company's Greenhouse board.

        Raises httpx.HTTPStatusError if Greenhouse answers with an error
        (for example 404 when the board token does not exist).
        """
        response = client.get(f"{BASE_URL}/{company.token}/jobs")
        response.raise_for_status()
        return response.json()["jobs"]

    def parse_job(self, raw: dict, company: Company) -> Job:
        """Turn one raw Greenhouse job dict into our normalized `Job`.

        See tests/fixtures/greenhouse_jobs.json for a real example. We use
        company.name instead of raw["company_name"] so names match across sources.
        """
        # "location" can be missing or None, and so can its "name".
        location = (raw.get("location") or {}).get("name") or "Unknown"
        return Job(
            source="greenhouse",
            external_id=str(raw["id"]),
            company=company.name,
            title=raw["title"].strip(),
            location=location,
            url=raw["absolute_url"],
            posted_at=raw.get("first_published"),  # ISO string; Pydantic parses it
        )
