"""Tests for refresh_jobs, using fake sources (no network)."""
from datetime import datetime, timezone

import httpx

from app.models import Company, Job
from app.refresh import refresh_jobs
from app.repository import list_active_jobs, save_company_jobs
from app.sources.base import JobSource
from tests.conftest import make_client

NOW = datetime(2026, 9, 28, tzinfo=timezone.utc)
GOOD = Company(name="Good", source="greenhouse", token="good")
BROKEN = Company(name="Broken", source="lever", token="broken")


class ListSource(JobSource):
    """Returns the given job ids, or fails like a 404 when ids is None."""

    name = "greenhouse"

    def __init__(self, ids: list[str] | None):
        self.ids = ids

    def fetch_raw(self, company, client):
        if self.ids is None:
            request = httpx.Request("GET", "https://example.com")
            raise httpx.HTTPStatusError("404", request=request, response=httpx.Response(404, request=request))
        return [{"id": i} for i in self.ids]

    def parse_job(self, raw, company):
        return Job(source=company.source, external_id=raw["id"], company=company.name, title=f"Role {raw['id']}", location="Remote", url="https://example.com")


def run_refresh(session, sources):
    with make_client(lambda request: httpx.Response(500)) as client:
        return refresh_jobs(session, [GOOD, BROKEN], client, sources, now=NOW)


def test_refresh_saves_jobs_and_reports_each_company(session):
    report = run_refresh(session, {"greenhouse": ListSource(["1", "2"]), "lever": ListSource(None)})

    assert [(r.company, r.status, r.added) for r in report] == [("Good", "ok", 2), ("Broken", "failed", 0)]
    assert sorted(job.external_id for job in list_active_jobs(session)) == ["1", "2"]


def test_failed_fetch_keeps_existing_jobs_active(session):
    """If a board is down, its saved jobs must not be marked as taken down."""
    save_company_jobs(session, BROKEN, [Job(source="lever", external_id="old", company="Broken", title="Role", location="Remote", url="https://example.com")], NOW)
    session.commit()

    run_refresh(session, {"greenhouse": ListSource(["1"]), "lever": ListSource(None)})

    assert [job.external_id for job in list_active_jobs(session, company="Broken")] == ["old"]
