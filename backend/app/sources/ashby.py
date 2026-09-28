"""Ashby adapter: fetch jobs from Ashby's public job posting API.

API docs: https://developers.ashbyhq.com/docs/public-job-posting-api
Endpoint:  GET https://api.ashbyhq.com/posting-api/job-board/{board_name}
No API key is needed.
"""
import httpx

from app.models import Company, Job
from app.sources.base import JobSource

BASE_URL = "https://api.ashbyhq.com/posting-api/job-board"


class AshbySource(JobSource):
    name = "ashby"

    def fetch_raw(self, company: Company, client: httpx.Client) -> list[dict]:
        """Return the raw job dicts for one company's Ashby board, listed jobs only."""
        response = client.get(f"{BASE_URL}/{company.token}")
        response.raise_for_status()
        # Skip jobs hidden from the public board.
        return [raw for raw in response.json()["jobs"] if raw.get("isListed", True)]

    def parse_job(self, raw: dict, company: Company) -> Job:
        """Turn one raw Ashby job into our normalized `Job`."""
        return Job(
            source="ashby",
            external_id=raw["id"],
            company=company.name,
            title=raw["title"].strip(),  # some Ashby titles have stray spaces
            location=raw.get("location") or "Unknown",
            url=raw["jobUrl"],
            posted_at=raw.get("publishedAt"),
        )
