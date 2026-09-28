"""Companies we fetch jobs for.

These were picked only because they have working public job boards (checked
2026-09-28). Their H-1B sponsorship history is NOT assumed here; Step 5 checks
it against government data (DOL LCA disclosures, USCIS H-1B Employer Data Hub).

How to find a token, from the company's careers page URL:
  greenhouse: boards.greenhouse.io/<token>
  lever:      jobs.lever.co/<token>
  ashby:      jobs.ashbyhq.com/<token>
  workday:    the whole URL, e.g. https://<tenant>.wd5.myworkdayjobs.com/<site>
"""
from app.models import Company

COMPANIES: list[Company] = [
    # Greenhouse
    Company(name="Stripe", source="greenhouse", token="stripe"),
    Company(name="Airbnb", source="greenhouse", token="airbnb"),
    Company(name="Figma", source="greenhouse", token="figma"),
    Company(name="Datadog", source="greenhouse", token="datadog"),
    Company(name="Coinbase", source="greenhouse", token="coinbase"),
    # Lever
    Company(name="Spotify", source="lever", token="spotify"),
    Company(name="Palantir", source="lever", token="palantir"),
    Company(name="Zoox", source="lever", token="zoox"),
    # Ashby
    Company(name="Ramp", source="ashby", token="ramp"),
    Company(name="Notion", source="ashby", token="notion"),
    Company(name="Linear", source="ashby", token="linear"),
    # Workday
    Company(name="NVIDIA", source="workday", token="https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"),
    Company(name="Salesforce", source="workday", token="https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"),
    Company(name="Capital One", source="workday", token="https://capitalone.wd12.myworkdayjobs.com/Capital_One"),
]
