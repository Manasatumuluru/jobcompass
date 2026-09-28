"""Tests for the JobSource base class."""
import pytest

from app.models import Company, Job
from app.sources.base import JobSource

COMPANY = Company(name="Acme", source="lever", token="acme")


def test_subclass_missing_a_method_cannot_be_created():
    class Incomplete(JobSource):
        name = "lever"

        def fetch_raw(self, company, client):
            return []

        # parse_job is missing

    with pytest.raises(TypeError, match="parse_job"):
        Incomplete()


def test_fetch_jobs_parses_each_raw_job():
    class Fake(JobSource):
        name = "lever"

        def fetch_raw(self, company, client):
            return [{"id": "1", "t": "Engineer"}, {"id": "2", "t": "Designer"}]

        def parse_job(self, raw, company):
            return Job(source=self.name, external_id=raw["id"], company=company.name, title=raw["t"], location="Remote", url="https://example.com")

    jobs = Fake().fetch_jobs(COMPANY, client=None)

    assert [(job.external_id, job.title, job.company) for job in jobs] == [("1", "Engineer", "Acme"), ("2", "Designer", "Acme")]
