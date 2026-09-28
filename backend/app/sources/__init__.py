"""Job source adapters: one module per career system.

Each module exposes the same function signature:

    fetch_jobs(company: Company, client: httpx.Client) -> list[Job]

so the rest of the app can treat every source the same way. To add a source,
write a module with that function and register it in SOURCES below.
"""
from collections.abc import Callable

import httpx

from app.models import Company, Job, SourceName
from app.sources import ashby, greenhouse, lever, workday

FetchJobs = Callable[[Company, httpx.Client], list[Job]]

SOURCES: dict[SourceName, FetchJobs] = {
    "greenhouse": greenhouse.fetch_jobs,
    "lever": lever.fetch_jobs,
    "ashby": ashby.fetch_jobs,
    "workday": workday.fetch_jobs,
}
