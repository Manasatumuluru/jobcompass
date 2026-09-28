"""Tests for duplicate removal."""
from datetime import datetime, timezone

from app.dedupe import dedupe_jobs, dedupe_key, normalize
from app.models import Job


def make_job(external_id="1", title="Software Engineer", location="Remote", company="Acme", source="greenhouse", posted_at=None) -> Job:
    return Job(source=source, external_id=external_id, company=company, title=title, location=location, url=f"https://example.com/{external_id}", posted_at=posted_at)


def day(n: int) -> datetime:
    return datetime(2026, 9, n, tzinfo=timezone.utc)


def test_normalize_ignores_case_punctuation_and_spaces():
    assert normalize("  Software Engineer, Backend (II) ") == "software engineer backend ii"
    assert normalize("Software engineer - backend II") == "software engineer backend ii"


def test_same_role_with_different_ids_is_one_key():
    a = make_job("1", title="Abuse Investigator", location="Dublin")
    b = make_job("2", title="abuse investigator", location="Dublin ")
    assert dedupe_key(a) == dedupe_key(b)


def test_different_location_or_company_is_not_a_duplicate():
    base = make_job("1")
    assert dedupe_key(base) != dedupe_key(make_job("2", location="New York"))
    assert dedupe_key(base) != dedupe_key(make_job("3", company="Other Co"))


def test_keeps_newest_and_input_order():
    old = make_job("1", posted_at=day(1))
    other = make_job("2", title="Designer")
    new = make_job("3", posted_at=day(5))

    result = dedupe_jobs([old, other, new])

    assert [job.external_id for job in result] == ["3", "2"]


def test_job_without_date_loses_to_dated_job():
    undated = make_job("1")
    dated = make_job("2", posted_at=day(1))

    assert [job.external_id for job in dedupe_jobs([dated, undated])] == ["2"]
    assert [job.external_id for job in dedupe_jobs([undated, dated])] == ["2"]


def test_same_role_on_two_sources_is_deduped():
    greenhouse = make_job("1", source="greenhouse", posted_at=day(2))
    lever = make_job("abc", source="lever", posted_at=day(1))

    assert [job.source for job in dedupe_jobs([greenhouse, lever])] == ["greenhouse"]
