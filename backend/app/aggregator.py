"""Collect jobs from every company, whatever system it uses."""
import logging
import time

import httpx
from pydantic import ValidationError

from app.models import Company, Job
from app.sources import SOURCES, JobSource

logger = logging.getLogger(__name__)

DELAY_SECONDS = 0.5  # be polite: small pause between companies


def fetch_all_jobs(
    companies: list[Company],
    client: httpx.Client,
    sources: dict[str, JobSource] = SOURCES,
) -> list[Job]:
    """Fetch and normalize jobs for every company in the list.

    Picks the right adapter for each company from `sources`. If one company
    fails (bad token, network error, unexpected data), log it and keep going,
    so one broken board does not hide jobs from the others.
    """
    jobs: list[Job] = []
    for i, company in enumerate(companies):
        if i > 0:
            time.sleep(DELAY_SECONDS)
        source = sources[company.source]
        try:
            jobs.extend(source.fetch_jobs(company, client))
        except (httpx.HTTPError, KeyError, ValidationError) as exc:
            logger.warning("Skipping %s (%s): %r", company.name, company.source, exc)
    return jobs
