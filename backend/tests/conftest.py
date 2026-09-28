"""Shared test helpers. pytest loads this file automatically."""
import json
from pathlib import Path

import httpx
import pytest

from app import aggregator
from app.sources import workday

FIXTURES = Path(__file__).parent / "fixtures"
USER_AGENT = "JobCompass-tests"


def load_fixture(name: str):
    """Read a saved real API response from tests/fixtures/."""
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def make_client(handler) -> httpx.Client:
    """A client whose requests go to `handler` instead of the internet."""
    return httpx.Client(transport=httpx.MockTransport(handler), headers={"User-Agent": USER_AGENT})


@pytest.fixture(autouse=True)
def no_delay(monkeypatch):
    """Skip the polite sleeps so tests run fast."""
    monkeypatch.setattr(aggregator, "DELAY_SECONDS", 0)
    monkeypatch.setattr(workday, "DELAY_SECONDS", 0)
