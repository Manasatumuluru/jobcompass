"""Tests for the Greenhouse adapter. No real network calls are made."""
from datetime import datetime

import httpx
import pytest

from app.models import Company
from app.sources.greenhouse import GreenhouseSource
from tests.conftest import USER_AGENT, load_fixture, make_client

STRIPE = Company(name="Stripe", source="greenhouse", token="stripe")
source = GreenhouseSource()


@pytest.fixture
def board_json() -> dict:
    return load_fixture("greenhouse_jobs.json")


def test_parse_job_maps_fields(board_json):
    job = source.parse_job(board_json["jobs"][0], STRIPE)

    assert job.source == "greenhouse"
    assert job.external_id == "8172487"
    assert job.company == "Stripe"
    assert job.title == "Abuse Investigator"
    assert job.location == "Dublin"
    assert job.url == "https://stripe.com/jobs/search?gh_jid=8172487"
    assert isinstance(job.posted_at, datetime)


def test_parse_job_missing_location(board_json):
    raw = board_json["jobs"][0] | {"location": None}
    assert source.parse_job(raw, STRIPE).location == "Unknown"

    raw_no_key = {k: v for k, v in board_json["jobs"][0].items() if k != "location"}
    assert source.parse_job(raw_no_key, STRIPE).location == "Unknown"


def test_fetch_jobs_calls_api(board_json):
    seen_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return httpx.Response(200, json=board_json)

    with make_client(handler) as client:
        jobs = source.fetch_jobs(STRIPE, client)

    assert len(jobs) == 2
    assert all(job.company == "Stripe" for job in jobs)
    assert str(seen_requests[0].url) == "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
    assert seen_requests[0].headers["User-Agent"] == USER_AGENT


def test_fetch_jobs_raises_on_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"status": 404, "error": "Job not found"})

    with make_client(handler) as client, pytest.raises(httpx.HTTPStatusError):
        source.fetch_jobs(STRIPE, client)
