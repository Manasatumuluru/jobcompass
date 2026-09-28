"""Data shapes shared across the app.

Every job source (Greenhouse, Lever, Ashby, Workday) turns its own JSON into
this one `Job` shape, so the rest of the app never has to care where a job
came from.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

SourceName = Literal["greenhouse", "lever", "ashby", "workday"]


class Job(BaseModel):
    """One job posting, normalized across all sources."""

    source: SourceName  # which system it came from
    external_id: str  # the job's id inside that source
    company: str  # our company name, from companies.py
    title: str
    location: str
    url: str  # link to the posting / apply page
    # When the job was first posted. None when the source does not give a
    # real date (Workday only says "Posted 30+ Days Ago"); we never guess.
    posted_at: datetime | None = None


class Company(BaseModel):
    """A company and where its jobs live.

    `token` means something different per source:
      greenhouse: board token     e.g. "stripe"
      lever:      site name       e.g. "spotify"
      ashby:      board name      e.g. "ramp"
      workday:    career site URL e.g. "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
    """

    name: str
    source: SourceName
    token: str
