# JobCompass — project guide for Claude Code

## What this project is
A web app that finds software roles asking for 0 to 4 years of experience at companies with a history of H-1B sponsorship.
Owner: Maan (full stack engineer). This is a **learning project** and a portfolio piece, so she must be able to explain every line in an interview.

## How to work with Maan (important)
- **Explain before you change.** Before editing, say in plain words what you will change and why. Keep it short.
- **Plan first.** For any new feature, propose a plan and wait for her approval before writing code.
- **Small steps.** One focused change at a time. After each change, tell her how to run or test it.
- **Leave one piece for her.** In each step, leave one small function as a `TODO(Maan)` with a docstring and hints, instead of writing it. Review her version when she finishes.
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
- Run API: `uvicorn app.main:app --reload` → http://127.0.0.1:8000/docs
- Tests: `pytest`

## Roadmap
1. [x] Project setup, FastAPI hello world
2. [ ] Fetch jobs from Greenhouse public job board API for ~5 companies
3. [ ] Lever, Ashby, Workday adapters sharing one normalized `Job` model (adapter pattern)
3b. [ ] Licensed aggregator APIs (JSearch for LinkedIn/Indeed listings, Adzuna). **Never scrape LinkedIn or Indeed directly.**
4. [ ] Store jobs in a database, deduplicate across sources
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
