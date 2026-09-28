"""Tests for the HTTP endpoints, using an in-memory database."""
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.db import get_session
from app.main import app
from app.models import Company, Job
from app.repository import save_company_jobs

NOW = datetime(2026, 9, 28, tzinfo=timezone.utc)
STRIPE = Company(name="Stripe", source="greenhouse", token="stripe")


@pytest.fixture
def client(session):
    """TestClient whose requests use the test database instead of jobcompass.db."""
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def stripe_job(external_id: str, title: str) -> Job:
    return Job(source="greenhouse", external_id=external_id, company="Stripe", title=title, location="Dublin", url=f"https://stripe.com/jobs/{external_id}")


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_jobs_empty_before_refresh(client):
    assert client.get("/jobs").json() == []


def test_jobs_returns_saved_jobs_without_duplicates(client, session):
    # Real Stripe case: two "Abuse Investigator" postings in Dublin with different ids.
    save_company_jobs(session, STRIPE, [
        stripe_job("8172487", "Abuse Investigator"),
        stripe_job("8172508", "Abuse Investigator"),
        stripe_job("9000000", "Software Engineer"),
    ], NOW)
    session.commit()

    jobs = client.get("/jobs").json()

    assert sorted(job["title"] for job in jobs) == ["Abuse Investigator", "Software Engineer"]


def test_jobs_filters(client, session):
    save_company_jobs(session, STRIPE, [stripe_job("1", "Software Engineer")], NOW)
    session.commit()

    assert len(client.get("/jobs", params={"company": "STRIPE"}).json()) == 1
    assert client.get("/jobs", params={"source": "lever"}).json() == []
    assert client.get("/jobs", params={"source": "indeed"}).status_code == 422
