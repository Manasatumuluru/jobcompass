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
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000/docs
