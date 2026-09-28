"""Tests for the Workday adapter. No real network calls are made."""
import json

import httpx
import pytest

from app.models import Company
from app.sources import workday
from app.sources.workday import fetch_jobs, parse_job, parse_site_url
from tests.conftest import load_fixture, make_client

SITE_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
NVIDIA = Company(name="NVIDIA", source="workday", token=SITE_URL)
API_URL = "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"


@pytest.fixture
def page_json() -> dict:
    return load_fixture("workday_jobs.json")


@pytest.mark.parametrize("url", [SITE_URL, SITE_URL + "/", "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite"])
def test_parse_site_url(url):
    assert parse_site_url(url) == ("nvidia.wd5.myworkdayjobs.com", "nvidia", "NVIDIAExternalCareerSite")


def test_parse_job_maps_fields(page_json):
    job = parse_job(page_json["jobPostings"][0], "NVIDIA", "nvidia.wd5.myworkdayjobs.com", "NVIDIAExternalCareerSite")

    assert job.source == "workday"
    assert job.external_id == "JR2015623"
    assert job.title == "Software Engineer, SPE"
    assert job.location == "Israel, Yokneam"
    assert job.url == SITE_URL + "/job/Israel-Yokneam/Software-Engineer--SPE_JR2015623"
    assert job.posted_at is None  # Workday gives no real date; we don't guess


def test_parse_job_without_bullet_fields_uses_path_as_id(page_json):
    raw = page_json["jobPostings"][0] | {"bulletFields": []}
    job = parse_job(raw, "NVIDIA", "nvidia.wd5.myworkdayjobs.com", "NVIDIAExternalCareerSite")

    assert job.external_id == "/job/Israel-Yokneam/Software-Engineer--SPE_JR2015623"


def test_fetch_jobs_stops_on_short_page(page_json):
    """The fixture page has 2 jobs (< 20), so only one request is made."""
    bodies = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == API_URL
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json=page_json)

    with make_client(handler) as client:
        jobs = fetch_jobs(NVIDIA, client)

    assert len(jobs) == 2
    assert bodies == [{"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "software engineer"}]


def test_fetch_jobs_pages_until_max_pages(page_json, monkeypatch):
    """Full pages keep coming, so it stops at MAX_PAGES."""
    monkeypatch.setattr(workday, "MAX_PAGES", 3)
    full_page = {"jobPostings": page_json["jobPostings"] * 10}  # 20 postings
    offsets = []

    def handler(request: httpx.Request) -> httpx.Response:
        offsets.append(json.loads(request.content)["offset"])
        return httpx.Response(200, json=full_page)

    with make_client(handler) as client:
        jobs = fetch_jobs(NVIDIA, client)

    assert offsets == [0, 20, 40]
    assert len(jobs) == 60
