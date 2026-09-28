"""Tests for fetch_all_jobs: routing to adapters and error handling.

These use fake adapters (plain functions) instead of HTTP, because the
aggregator should not care how an adapter gets its jobs.
"""
import httpx

from app.aggregator import fetch_all_jobs
from app.models import Company, Job
from tests.conftest import make_client


def fake_job(company: Company) -> Job:
    return Job(source=company.source, external_id="1", company=company.name, title="Engineer", location="Remote", url="https://example.com/1")


def ok_adapter(company, client):
    return [fake_job(company)]


def failing_adapter(company, client):
    request = httpx.Request("GET", "https://example.com")
    raise httpx.HTTPStatusError("404", request=request, response=httpx.Response(404, request=request))


def test_routes_each_company_to_its_source():
    calls = []

    def recording_adapter(company, client):
        calls.append(company.name)
        return [fake_job(company)]

    companies = [
        Company(name="A", source="greenhouse", token="a"),
        Company(name="B", source="lever", token="b"),
    ]
    sources = {"greenhouse": recording_adapter, "lever": ok_adapter}

    with make_client(lambda request: httpx.Response(500)) as client:
        jobs = fetch_all_jobs(companies, client, sources)

    assert calls == ["A"]
    assert [(job.company, job.source) for job in jobs] == [("A", "greenhouse"), ("B", "lever")]


def test_skips_failed_company_and_keeps_others():
    companies = [
        Company(name="Broken", source="greenhouse", token="nope"),
        Company(name="Works", source="ashby", token="ok"),
    ]
    sources = {"greenhouse": failing_adapter, "ashby": ok_adapter}

    with make_client(lambda request: httpx.Response(500)) as client:
        jobs = fetch_all_jobs(companies, client, sources)

    assert [job.company for job in jobs] == ["Works"]


def test_skips_company_with_unexpected_data():
    def bad_data_adapter(company, client):
        return [{}["title"]]  # KeyError, like a response missing a field

    companies = [
        Company(name="Weird", source="lever", token="x"),
        Company(name="Works", source="ashby", token="ok"),
    ]
    sources = {"lever": bad_data_adapter, "ashby": ok_adapter}

    with make_client(lambda request: httpx.Response(500)) as client:
        jobs = fetch_all_jobs(companies, client, sources)

    assert [job.company for job in jobs] == ["Works"]
