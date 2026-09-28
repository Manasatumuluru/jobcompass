"""Tests for the Ashby adapter. No real network calls are made."""
from datetime import datetime

import httpx
import pytest

from app.models import Company
from app.sources.ashby import AshbySource
from tests.conftest import load_fixture, make_client

RAMP = Company(name="Ramp", source="ashby", token="ramp")
source = AshbySource()


@pytest.fixture
def board_json() -> dict:
    return load_fixture("ashby_jobs.json")


def test_parse_job_maps_fields_and_strips_title(board_json):
    job = source.parse_job(board_json["jobs"][0], RAMP)  # real title is " Security Engineer, Cloud"

    assert job.source == "ashby"
    assert job.external_id == "34413f8d-26bf-4bbc-8ade-eb309a0e2245"
    assert job.title == "Security Engineer, Cloud"
    assert job.location == "New York, NY (HQ)"
    assert job.url == "https://jobs.ashbyhq.com/ramp/34413f8d-26bf-4bbc-8ade-eb309a0e2245"
    assert isinstance(job.posted_at, datetime)


def test_fetch_jobs_skips_unlisted(board_json):
    board_json["jobs"][1]["isListed"] = False
    seen_urls = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json=board_json)

    with make_client(handler) as client:
        jobs = source.fetch_jobs(RAMP, client)

    assert [job.external_id for job in jobs] == ["34413f8d-26bf-4bbc-8ade-eb309a0e2245"]
    assert seen_urls == ["https://api.ashbyhq.com/posting-api/job-board/ramp"]
