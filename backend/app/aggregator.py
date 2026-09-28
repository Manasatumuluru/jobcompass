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
) -> dict[str, list[Job]]:
    """Fetch and normalize jobs for every company in the list.

    Returns {company name: jobs} for the companies that succeeded. A company
    that failed (bad token, network error, unexpected data) is logged and
    left out, so the caller can tell "fetch failed" apart from "no jobs".
    """
    results: dict[str, list[Job]] = {}
    for i, company in enumerate(companies):
        if i > 0:
            time.sleep(DELAY_SECONDS)
        source = sources[company.source]
        try:
            results[company.name] = source.fetch_jobs(company, client)
        except (httpx.HTTPError, KeyError, ValidationError) as exc:
            logger.warning("Skipping %s (%s): %r", company.name, company.source, exc)
    return results
