"""Job source adapters: one module per career system.

Each adapter is a subclass of `JobSource` (see base.py). To add a source,
write a subclass with `fetch_raw` and `parse_job`, and add it to SOURCES below.
"""
from app.models import SourceName
from app.sources.ashby import AshbySource
from app.sources.base import JobSource
from app.sources.greenhouse import GreenhouseSource
from app.sources.lever import LeverSource
from app.sources.workday import WorkdaySource

SOURCES: dict[SourceName, JobSource] = {
    source.name: source
    for source in [GreenhouseSource(), LeverSource(), AshbySource(), WorkdaySource()]
}
