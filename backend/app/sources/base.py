"""The shared base class every job source adapter extends."""
from abc import ABC, abstractmethod

import httpx

from app.models import Company, Job, SourceName


class JobSource(ABC):
    """One career system (Greenhouse, Lever, ...), adapted to our `Job` model.

    Subclasses fill in two steps: how to fetch raw jobs from their API
    (`fetch_raw`) and how to translate one raw job (`parse_job`). The shared
    recipe that joins them (`fetch_jobs`) lives here, written once.
    """

    name: SourceName  # e.g. "greenhouse"; must match Company.source

    @abstractmethod
    def fetch_raw(self, company: Company, client: httpx.Client) -> list[dict]:
        """Call the source's API and return its raw job dicts."""

    @abstractmethod
    def parse_job(self, raw: dict, company: Company) -> Job:
        """Turn one raw job dict into our normalized `Job`."""

    def fetch_jobs(self, company: Company, client: httpx.Client) -> list[Job]:
        """All jobs for one company, normalized. Same for every source."""
        return [self.parse_job(raw, company) for raw in self.fetch_raw(company, client)]
