"""Remove duplicate job postings.

Companies often post the same role several times (one per opening, or on
two systems), with different ids. Stripe's real board has two separate
"Abuse Investigator, Dublin" postings, for example. A job seeker only
needs to see it once.

Two jobs are duplicates when company, title and location match after
normalizing (lowercase, punctuation and extra spaces removed).
"""
import re

from app.models import Job


def normalize(text: str) -> str:
    """ "Software Engineer, Backend (II)" -> "software engineer backend ii" """
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def dedupe_key(job: Job) -> str:
    return "|".join(normalize(part) for part in (job.company, job.title, job.location))


def _is_newer(job: Job, other: Job) -> bool:
    """True if `job` has a later posted date than `other`. No date counts as oldest."""
    if job.posted_at is None:
        return False
    return other.posted_at is None or job.posted_at > other.posted_at


def dedupe_jobs(jobs: list[Job]) -> list[Job]:
    """Keep one job per dedupe key: the most recently posted one.

    Keeps the order of the input (each key stays where it first appeared).
    """
    best: dict[str, Job] = {}
    for job in jobs:
        key = dedupe_key(job)
        if key not in best or _is_newer(job, best[key]):
            best[key] = job
    return list(best.values())
