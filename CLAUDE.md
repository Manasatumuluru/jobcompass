# JobCompass — project guide for Claude Code

## What this project is
A web app that finds software roles asking for 0 to 4 years of experience at companies with a history of H-1B sponsorship.
Owner: Maan (full stack engineer). This is a **learning project** and a portfolio piece, so she must be able to explain every line in an interview.

## How to work with Maan (important)
- **Build the whole step, then explain.** For each roadmap step, write all the code (no `TODO(Maan)` stubs), test it, commit it, then explain it: what each file does, a line-by-line walkthrough of the tricky parts, and how to run or test it.
- **Small steps.** Keep each commit focused on one roadmap step.
- **Teach the concept.** When you use a pattern or library for the first time (adapter pattern, dependency injection, ORM, etc.), explain it in 2 to 3 sentences.
- **End each step with 2 to 3 interview-style questions** about what was built.
- **Never invent data.** Sponsorship info must come from real government data (DOL LCA disclosures, USCIS H-1B Employer Data Hub). Never hardcode or guess it.
- Simple words. Maan prefers clear, direct explanations.

## Stack
- Backend: Python 3.12, FastAPI, Uvicorn, SQLAlchemy, PostgreSQL (SQLite allowed for local dev), pytest
- Frontend (later): React + TypeScript (Vite)
- Deploy (later): AWS
- OS: Windows. Use PowerShell commands in instructions.

## Commands (run from `backend/` with the venv active)
- Create venv: `py -3.12 -m venv .venv`
- Activate: `.venv\Scripts\activate`
- Install: `pip install -r requirements.txt`
- Load jobs into the database: `python -m app.refresh` (or `POST /refresh`)
- Run API: `uvicorn app.main:app --reload` → http://127.0.0.1:8000/docs
- Tests: `pytest`

## Roadmap
1. [x] Project setup, FastAPI hello world
2. [x] Fetch jobs from Greenhouse public job board API for ~5 companies
3. [x] Lever, Ashby, Workday adapters sharing one normalized `Job` model (adapter pattern)
3b. [ ] Licensed aggregator APIs (JSearch for LinkedIn/Indeed listings, Adzuna). **Never scrape LinkedIn or Indeed directly.**
4. [x] Store jobs in a database, deduplicate across sources
5. [ ] Load H-1B government data, fuzzy-match employer names to companies
6. [ ] Experience (0–4 yrs) and skill filters, match score
7. [ ] React UI with filters and job cards
8. [ ] Daily scheduled refresh
9. [ ] Deploy to AWS
10. [ ] User accounts, saved jobs, Claude API match explanations

## Rules
- Respect API rate limits; add a User-Agent and small delays when fetching.
- Secrets go in `.env` (git-ignored). Never commit keys.
- The UI must say sponsorship history is not a guarantee and is not legal advice.
- Commit after each working change with a clear message.
