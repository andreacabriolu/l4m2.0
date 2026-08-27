import os
import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()

for parent in CURRENT_FILE.parents:
    if (parent / "manage.py").exists():
        PROJECT_ROOT = parent
        break
else:
    raise RuntimeError(
        "Django project root not found"
    )

sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "l4m20.settings"
)

import django
django.setup()

from zoneinfo import ZoneInfo
from icalendar import Calendar
import requests
from l4m_app.utilities import get_real_team_by_name
import l4m20.constants as C
from l4m_app.single_models import real_calendar
from django.db.models import Q

ICS_URL = "https://www.matchesio.com/it/competition/serie-a-it/export/ics/"

response = requests.get(
    ICS_URL,
    timeout=30
)

response.raise_for_status()

ics_content = response.text

calendar = Calendar.from_ical(ics_content)

for event in calendar.walk("VEVENT"):
    summary = event.get("SUMMARY")
    dtstart = event.get("DTSTART").dt.astimezone(ZoneInfo(key='Europe/Rome'))
    uid = event.get("UID")

    now = django.utils.timezone.now()

    if dtstart < now:
        continue

    teams = summary.split(" - ")

    if len(teams) != 2:
        continue

    home_team = get_real_team_by_name(C.Mappings.TEAM_NAMES_MAPPING.get(teams[0].strip().lower(), teams[0].strip()))
    away_team = get_real_team_by_name(C.Mappings.TEAM_NAMES_MAPPING.get(teams[1].strip().lower(), teams[1].strip()))
    real_match = real_calendar.Real_calendar.objects.filter(
        Q(RealTeamHome=home_team) & 
        Q(RealTeamAway=away_team) &
        Q(Season__Active=True)).first()

    if real_match is None:
        continue

    real_match.Date = dtstart
    
    real_match.save(update_fields=['Date', 'FT'])    

    # print (f"Updated match: {home_team} vs {away_team} on {dtstart.astimezone(ZoneInfo(key='Europe/Rome')).strftime('%d-%m-%Y alle %H:%M')}")

print("Calendars updated successfully.")
