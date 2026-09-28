"""Tests for saving and reading jobs (in-memory SQLite)."""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db_models import JobRow
from app.models import Company, Job
from app.repository import list_active_jobs, save_company_jobs

ACME = Company(name="Acme", source="greenhouse", token="acme")
OTHER = Company(name="Other", source="lever", token="other")
NOW = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)


def make_job(external_id: str, company: Company = ACME, title="Engineer", posted_at=None) -> Job:
    return Job(source=company.source, external_id=external_id, company=company.name, title=title, location="Remote", url=f"https://example.com/{external_id}", posted_at=posted_at)


def test_first_save_adds_jobs(session):
    counts = save_company_jobs(session, ACME, [make_job("1"), make_job("2")], NOW)
    session.commit()

    assert (counts.added, counts.updated, counts.deactivated) == (2, 0, 0)
    assert [job.external_id for job in list_active_jobs(session)] == ["1", "2"]


def test_second_save_updates_adds_and_deactivates(session):
    save_company_jobs(session, ACME, [make_job("1"), make_job("2")], NOW)
    session.commit()

    later = NOW + timedelta(days=1)
    counts = save_company_jobs(session, ACME, [make_job("1", title="Senior Engineer"), make_job("3")], later)
    session.commit()

    assert (counts.added, counts.updated, counts.deactivated) == (1, 1, 1)
    active = {job.external_id: job for job in list_active_jobs(session)}
    assert set(active) == {"1", "3"}
    assert active["1"].title == "Senior Engineer"

    gone = session.scalars(select(JobRow).where(JobRow.external_id == "2")).one()
    assert gone.is_active is False  # kept, not deleted

    kept = session.scalars(select(JobRow).where(JobRow.external_id == "1")).one()
    assert kept.first_seen_at == NOW.replace(tzinfo=None)
    assert kept.last_seen_at == later.replace(tzinfo=None)


def test_job_that_comes_back_is_active_again(session):
    save_company_jobs(session, ACME, [make_job("1")], NOW)
    save_company_jobs(session, ACME, [], NOW)
    save_company_jobs(session, ACME, [make_job("1")], NOW)
    session.commit()

    assert [job.external_id for job in list_active_jobs(session)] == ["1"]


def test_saving_one_company_does_not_touch_another(session):
    save_company_jobs(session, ACME, [make_job("1")], NOW)
    save_company_jobs(session, OTHER, [make_job("1", company=OTHER)], NOW)
    save_company_jobs(session, ACME, [], NOW)  # Acme's job is gone
    session.commit()

    assert [(job.company, job.external_id) for job in list_active_jobs(session)] == [("Other", "1")]


def test_duplicate_id_in_one_response_is_saved_once(session):
    counts = save_company_jobs(session, ACME, [make_job("1"), make_job("1")], NOW)
    session.commit()

    assert counts.added == 1


def test_posted_at_round_trips_as_utc(session):
    posted = datetime(2026, 9, 25, 16, 45, tzinfo=timezone(timedelta(hours=-4)))  # 20:45 UTC
    save_company_jobs(session, ACME, [make_job("1", posted_at=posted)], NOW)
    session.commit()

    job = list_active_jobs(session)[0]
    assert job.posted_at == posted  # same moment in time
    assert job.posted_at.tzinfo == timezone.utc
    assert job.posted_at.hour == 20


def test_list_filters_and_order(session):
    save_company_jobs(session, ACME, [
        make_job("old", posted_at=NOW - timedelta(days=5)),
        make_job("undated"),
        make_job("new", posted_at=NOW),
    ], NOW)
    save_company_jobs(session, OTHER, [make_job("x", company=OTHER)], NOW)
    session.commit()

    assert [job.external_id for job in list_active_jobs(session, company="acme")] == ["new", "old", "undated"]
    assert [job.external_id for job in list_active_jobs(session, source="lever")] == ["x"]
