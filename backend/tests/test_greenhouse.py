"""Tests for the Greenhouse adapter. No real network calls are made."""
import json
from datetime import datetime
from pathlib import Path

import httpx
import pytest

from app.sources import greenhouse
from app.sources.greenhouse import fetch_greenhouse_jobs, parse_job

FIXTURE = Path(__file__).parent / "fixtures" / "greenhouse_jobs.json"
USER_AGENT = "JobCompass-tests"


@pytest.fixture
def board_json() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def no_delay(monkeypatch):
    """Skip the polite sleep so tests run fast."""
    monkeypatch.setattr(greenhouse, "DELAY_SECONDS", 0)


def make_client(handler) -> httpx.Client:
    """A client whose requests go to `handler` instead of the internet."""
    return httpx.Client(transport=httpx.MockTransport(handler), headers={"User-Agent": USER_AGENT})


def test_parse_job_maps_fields(board_json):
    job = parse_job(board_json["jobs"][0], "Stripe")

    assert job.source == "greenhouse"
    assert job.external_id == "8172487"
    assert job.company == "Stripe"
    assert job.title == "Abuse Investigator"
    assert job.location == "Dublin"
    assert job.url == "https://stripe.com/jobs/search?gh_jid=8172487"
    assert isinstance(job.updated_at, datetime)


def test_parse_job_missing_location(board_json):
    raw = board_json["jobs"][0] | {"location": None}
    assert parse_job(raw, "Stripe").location == "Unknown"

    raw_no_key = {k: v for k, v in board_json["jobs"][0].items() if k != "location"}
    assert parse_job(raw_no_key, "Stripe").location == "Unknown"


def test_fetch_greenhouse_jobs_calls_api(board_json):
    seen_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(200, json=board_json)

    with make_client(handler) as client:
        jobs = fetch_greenhouse_jobs([{"name": "Stripe", "board_token": "stripe"}], client)

    assert len(jobs) == 2
    assert all(job.company == "Stripe" for job in jobs)
    assert str(seen_requests[0].url) == "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
    assert seen_requests[0].headers["User-Agent"] == USER_AGENT


def test_fetch_greenhouse_jobs_skips_failed_company(board_json):
    def handler(request: httpx.Request) -> httpx.Response:
        if "/not-a-real-board/" in request.url.path:
            return httpx.Response(404, json={"status": 404, "error": "Job not found"})
        return httpx.Response(200, json=board_json)

    companies = [
        {"name": "Broken", "board_token": "not-a-real-board"},
        {"name": "Stripe", "board_token": "stripe"},
    ]
    with make_client(handler) as client:
        jobs = fetch_greenhouse_jobs(companies, client)

    assert len(jobs) == 2
    assert {job.company for job in jobs} == {"Stripe"}
