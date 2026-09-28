"""Read and write jobs in the database.

The rest of the app works with Pydantic `Job` objects; only this file
knows about `JobRow` and SQL.
"""
from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db_models import JobRow
from app.models import Company, Job


class SaveCounts(BaseModel):
    added: int = 0
    updated: int = 0
    deactivated: int = 0


def to_db_time(value: datetime | None) -> datetime | None:
    """Timezone-aware datetime -> naive UTC (what we store)."""
    return value.astimezone(timezone.utc).replace(tzinfo=None) if value else None


def from_db_time(value: datetime | None) -> datetime | None:
    """Naive UTC from the database -> timezone-aware UTC."""
    return value.replace(tzinfo=timezone.utc) if value else None


def row_to_job(row: JobRow) -> Job:
    return Job(
        source=row.source,
        external_id=row.external_id,
        company=row.company,
        title=row.title,
        location=row.location,
        url=row.url,
        posted_at=from_db_time(row.posted_at),
    )


def save_company_jobs(session: Session, company: Company, jobs: list[Job], seen_at: datetime) -> SaveCounts:
    """Store the jobs just fetched for one company (an "upsert").

    - New job ids are inserted.
    - Known job ids are updated (title/location can change) and marked active.
    - This company's jobs that were NOT in `jobs` are marked inactive: they
      were taken down. We keep the row instead of deleting it.

    Call this only when the fetch succeeded; otherwise every job would look
    taken down. The caller commits.
    """
    counts = SaveCounts()
    seen_at = to_db_time(seen_at)
    existing = {
        row.external_id: row
        for row in session.scalars(
            select(JobRow).where(JobRow.source == company.source, JobRow.company == company.name)
        )
    }

    seen_ids: set[str] = set()
    for job in jobs:
        if job.external_id in seen_ids:  # same id twice in one response
            continue
        seen_ids.add(job.external_id)

        row = existing.get(job.external_id)
        if row is None:
            row = JobRow(source=job.source, company=company.name, external_id=job.external_id, first_seen_at=seen_at)
            session.add(row)
            counts.added += 1
        else:
            counts.updated += 1
        row.title = job.title
        row.location = job.location
        row.url = job.url
        row.posted_at = to_db_time(job.posted_at)
        row.is_active = True
        row.last_seen_at = seen_at

    for external_id, row in existing.items():
        if external_id not in seen_ids and row.is_active:
            row.is_active = False
            counts.deactivated += 1

    return counts


def list_active_jobs(session: Session, source: str | None = None, company: str | None = None) -> list[Job]:
    """Active jobs, newest first (jobs with no date last). Filters are optional."""
    query = select(JobRow).where(JobRow.is_active)
    if source:
        query = query.where(JobRow.source == source)
    if company:
        query = query.where(func.lower(JobRow.company) == company.lower())
    query = query.order_by(JobRow.posted_at.desc().nulls_last(), JobRow.id)
    return [row_to_job(row) for row in session.scalars(query)]
