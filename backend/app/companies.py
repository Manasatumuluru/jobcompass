"""Companies we fetch jobs for.

These were picked only because they have working public Greenhouse boards.
Their H-1B sponsorship history is NOT assumed here; Step 5 checks it against
government data (DOL LCA disclosures, USCIS H-1B Employer Data Hub).

To add a company, find its board token in its Greenhouse careers URL:
boards.greenhouse.io/<board_token>
"""

GREENHOUSE_COMPANIES: list[dict[str, str]] = [
    {"name": "Stripe", "board_token": "stripe"},
    {"name": "Airbnb", "board_token": "airbnb"},
    {"name": "Figma", "board_token": "figma"},
    {"name": "Datadog", "board_token": "datadog"},
    {"name": "Coinbase", "board_token": "coinbase"},
]
