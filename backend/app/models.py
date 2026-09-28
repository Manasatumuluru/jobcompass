"""Data shapes shared across the app.

Every job source (Greenhouse now; Lever, Ashby, Workday later) turns its own
JSON into this one `Job` shape, so the rest of the app never has to care
where a job came from.
"""
from datetime import datetime

from pydantic import BaseModel


class Job(BaseModel):
    """One job posting, normalized across all sources."""

    source: str  # which system it came from, e.g. "greenhouse"
    external_id: str  # the job's id inside that source
    company: str  # our company name, from companies.py
    title: str
    location: str
    url: str  # link to the posting / apply page
    updated_at: datetime
