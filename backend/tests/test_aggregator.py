"""Tests for fetch_all_jobs: routing to adapters and error handling.

These use fake JobSource subclasses instead of HTTP, because the aggregator
should not care how an adapter gets its jobs.
"""
import httpx

from app.aggregator import fetch_all_jobs
from app.models import Company, Job
from app.sources.base import JobSource
from tests.conftest import make_client


class OkSource(JobSource):
    """Returns one job per company and remembers which companies it saw."""

    name = "greenhouse"

    def __init__(self):
        self.seen = []

    def fetch_raw(self, company, client):
        self.seen.append(company.name)
        return [{"id": "1"}]

    def parse_job(self, raw, company):
        return Job(source=company.source, external_id=raw["id"], company=company.name, title="Engineer", location="Remote", url="https://example.com/1")


class FailingSource(OkSource):
    """Answers like a board that does not exist."""

    def fetch_raw(self, company, client):
        request = httpx.Request("GET", "https://example.com")
        raise httpx.HTTPStatusError("404", request=request, response=httpx.Response(404, request=request))


class BadDataSource(OkSource):
    """Returns a job missing a field we need (raw["id"] -> KeyError)."""

    def fetch_raw(self, company, client):
        return [{}]


def run(companies, sources) -> dict[str, list[Job]]:
    with make_client(lambda request: httpx.Response(500)) as client:
        return fetch_all_jobs(companies, client, sources)


def test_routes_each_company_to_its_source():
    greenhouse, lever = OkSource(), OkSource()
    companies = [
        Company(name="A", source="greenhouse", token="a"),
        Company(name="B", source="lever", token="b"),
    ]

    results = run(companies, {"greenhouse": greenhouse, "lever": lever})

    assert greenhouse.seen == ["A"]
    assert lever.seen == ["B"]
    assert [job.source for job in results["A"]] == ["greenhouse"]
    assert [job.source for job in results["B"]] == ["lever"]


def test_failed_company_is_left_out_others_kept():
    companies = [
        Company(name="Broken", source="greenhouse", token="nope"),
        Company(name="Works", source="ashby", token="ok"),
    ]

    results = run(companies, {"greenhouse": FailingSource(), "ashby": OkSource()})

    assert list(results) == ["Works"]


def test_company_with_unexpected_data_is_left_out():
    companies = [
        Company(name="Weird", source="lever", token="x"),
        Company(name="Works", source="ashby", token="ok"),
    ]

    results = run(companies, {"lever": BadDataSource(), "ashby": OkSource()})

    assert list(results) == ["Works"]
