"""Fetch every company's jobs and save them to the database.

Run it from the backend folder:
    python -m app.refresh
The API's POST /refresh does the same. Step 8 will run it on a daily schedule.
"""
import logging
from datetime import datetime, timezone
from typing import Literal

import httpx
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.aggregator import fetch_all_jobs
from app.companies import COMPANIES
from app.db import SessionLocal, init_db
from app.models import Company
from app.repository import SaveCounts, save_company_jobs
from app.sources import SOURCES, JobSource

USER_AGENT = "JobCompass/0.1 (learning project)"


class CompanyRefresh(SaveCounts):
    """What happened to one company during a refresh."""

    company: str
    source: str
    status: Literal["ok", "failed"]


def make_http_client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=10.0)


def refresh_jobs(
    session: Session,
    companies: list[Company],
    client: httpx.Client,
    sources: dict[str, JobSource] = SOURCES,
    now: datetime | None = None,
) -> list[CompanyRefresh]:
    """Fetch all companies, save the ones that succeeded, and commit.

    A failed company's saved jobs are left untouched (not marked inactive),
    because a failed fetch tells us nothing about which jobs are gone.
    """
    now = now or datetime.now(timezone.utc)
    results = fetch_all_jobs(companies, client, sources)

    report: list[CompanyRefresh] = []
    for company in companies:
        if company.name not in results:
            report.append(CompanyRefresh(company=company.name, source=company.source, status="failed"))
            continue
        counts = save_company_jobs(session, company, results[company.name], now)
        report.append(CompanyRefresh(company=company.name, source=company.source, status="ok", **counts.model_dump()))
    session.commit()
    return report


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)  # hide one log line per request
    init_db()
    with SessionLocal() as session, make_http_client() as client:
        report = refresh_jobs(session, COMPANIES, client)
    for r in report:
        print(f"{r.company:12} {r.source:10} {r.status:6} +{r.added} ~{r.updated} -{r.deactivated}")


if __name__ == "__main__":
    main()
