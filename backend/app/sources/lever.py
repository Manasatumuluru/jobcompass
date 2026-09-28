"""Lever adapter: fetch jobs from Lever's public postings API.

API docs: https://github.com/lever/postings-api
Endpoint:  GET https://api.lever.co/v0/postings/{site}?mode=json
No API key is needed. The response is a JSON list (not an object).
"""
from datetime import datetime, timezone

import httpx

from app.models import Company, Job
from app.sources.base import JobSource

BASE_URL = "https://api.lever.co/v0/postings"


class LeverSource(JobSource):
    name = "lever"

    def fetch_raw(self, company: Company, client: httpx.Client) -> list[dict]:
        """Return the raw posting dicts for one company's Lever site."""
        response = client.get(f"{BASE_URL}/{company.token}", params={"mode": "json"})
        response.raise_for_status()
        return response.json()

    def parse_job(self, raw: dict, company: Company) -> Job:
        """Turn one raw Lever posting into our normalized `Job`.

        See tests/fixtures/lever_postings.json for two real examples.
        """
        location = (raw.get("categories") or {}).get("location") or "Unknown"
        # Lever gives createdAt as milliseconds since 1970 (Unix time), in UTC.
        created_ms = raw.get("createdAt")
        posted_at = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc) if created_ms else None
        return Job(
            source="lever",
            external_id=raw["id"],
            company=company.name,
            title=raw["text"].strip(),  # Lever calls the title "text"
            location=location,
            url=raw["hostedUrl"],
            posted_at=posted_at,
        )
