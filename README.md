# JobCompass

Finds software roles asking for 0 to 4 years of experience at companies with a history of H-1B sponsorship.
Jobs come directly from company career systems (Greenhouse, Lever, Ashby, Workday) and licensed job data APIs.

> Sponsorship history is based on public government data and is not a guarantee of future sponsorship. Not legal advice.

## Run locally (Windows)

```
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.refresh
uvicorn app.main:app --reload
```

`python -m app.refresh` fetches jobs from every company's board (about 30 seconds) and saves them to a local SQLite file, `jobcompass.db`. Run it again any time to update the jobs.

Then open http://127.0.0.1:8000/docs
