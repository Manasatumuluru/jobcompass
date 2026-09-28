"""Entry point for the H1B Job Finder API.

Run from the backend folder with:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI

app = FastAPI(
    title="H1B Job Finder",
    description="Finds 0-4 year roles at companies with H-1B sponsorship history.",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict:
    """Simple check that the server is running. Deploy tools ping this."""
    return {"status": "ok"}


@app.get("/jobs")
def list_jobs() -> list[dict]:
    """Returns jobs. For now it is fake data; Step 2 replaces it with real postings."""
    return [
        {
            "company": "Example Corp",
            "title": "Software Engineer I",
            "location": "Houston, TX",
            "years_required": "0-2",
            "h1b_history": True,
        }
    ]
