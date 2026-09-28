"""Tests for the Lever adapter. No real network calls are made."""
from datetime import timezone

import httpx
import pytest

from app.models import Company
from app.sources.lever import fetch_jobs, parse_job
from tests.conftest import load_fixture, make_client

SPOTIFY = Company(name="Spotify", source="lever", token="spotify")


@pytest.fixture
def postings() -> list[dict]:
    return load_fixture("lever_postings.json")


def test_parse_job_maps_fields(postings):
    job = parse_job(postings[0], "Spotify")

    assert job.source == "lever"
    assert job.external_id == "2193db3f-77c5-43b8-b030-8f92c9882bf1"
    assert job.title == "Android Engineer - Experience"
    assert job.location == "London"
    assert job.url == "https://jobs.lever.co/spotify/2193db3f-77c5-43b8-b030-8f92c9882bf1"


def test_parse_job_converts_milliseconds_to_utc_datetime(postings):
    job = parse_job(postings[0], "Spotify")  # createdAt = 1782214185805 ms

    assert job.posted_at.tzinfo == timezone.utc
    assert job.posted_at.timestamp() == pytest.approx(1782214185.805)


def test_parse_job_missing_date_and_location(postings):
    raw = postings[0] | {"categories": {}, "createdAt": None}
    job = parse_job(raw, "Spotify")

    assert job.location == "Unknown"
    assert job.posted_at is None


def test_fetch_jobs_uses_json_mode(postings):
    seen_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json=postings)

    with make_client(handler) as client:
        jobs = fetch_jobs(SPOTIFY, client)

    assert len(jobs) == 2
    assert seen_urls == ["https://api.lever.co/v0/postings/spotify?mode=json"]
