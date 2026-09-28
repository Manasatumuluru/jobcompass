"""Workday adapter: fetch jobs from a company's Workday career site.

Workday has no official public API for job boards. Every Workday career site
loads its job list from this JSON endpoint in the browser, and we call the same
one, politely (User-Agent, delays, a page cap):

    POST https://{host}/wday/cxs/{tenant}/{site}/jobs
    body: {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": "..."}

Big companies have thousands of jobs, 20 per page, so we search for software
roles only and stop after MAX_PAGES pages.
"""
import logging
import time

import httpx

from app.models import Company, Job
from app.sources.base import JobSource

logger = logging.getLogger(__name__)

PAGE_SIZE = 20  # Workday rejects bigger pages with HTTP 400
MAX_PAGES = 5  # at most 100 jobs per company per refresh
SEARCH_TEXT = "software engineer"
DELAY_SECONDS = 0.5  # pause between pages


def parse_site_url(site_url: str) -> tuple[str, str, str]:
    """Split a career site URL into (host, tenant, site).

    "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
      -> ("nvidia.wd5.myworkdayjobs.com", "nvidia", "NVIDIAExternalCareerSite")
    Also works with a language part: ".../en-US/NVIDIAExternalCareerSite".
    """
    url = httpx.URL(site_url)
    host = url.host
    tenant = host.split(".")[0]
    site = url.path.strip("/").split("/")[-1]
    return host, tenant, site


class WorkdaySource(JobSource):
    name = "workday"

    def fetch_raw(self, company: Company, client: httpx.Client) -> list[dict]:
        """Return raw software job postings for one company, page by page."""
        host, tenant, site = parse_site_url(company.token)
        api_url = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"

        postings: list[dict] = []
        for page in range(MAX_PAGES):
            if page > 0:
                time.sleep(DELAY_SECONDS)
            body = {"appliedFacets": {}, "limit": PAGE_SIZE, "offset": page * PAGE_SIZE, "searchText": SEARCH_TEXT}
            response = client.post(api_url, json=body)
            response.raise_for_status()
            page_postings = response.json().get("jobPostings") or []
            postings.extend(page_postings)
            if len(page_postings) < PAGE_SIZE:  # a short page means it was the last one
                return postings

        logger.info("%s: stopped after %d pages (%d jobs); more exist", company.name, MAX_PAGES, len(postings))
        return postings

    def parse_job(self, raw: dict, company: Company) -> Job:
        """Turn one raw Workday posting into our normalized `Job`."""
        host, _tenant, site = parse_site_url(company.token)
        path = raw["externalPath"]  # e.g. "/job/US-Remote/Software-Engineer_JR2020825"
        bullet_fields = raw.get("bulletFields") or []
        return Job(
            source="workday",
            # bulletFields[0] is the requisition id (e.g. "JR2020825") when present.
            external_id=bullet_fields[0] if bullet_fields else path,
            company=company.name,
            title=raw["title"].strip(),
            # Can be a place or a summary like "3 Locations"; we keep what Workday says.
            location=raw.get("locationsText") or "Unknown",
            url=f"https://{host}/{site}{path}",
            posted_at=None,  # Workday only gives text like "Posted 30+ Days Ago"
        )
