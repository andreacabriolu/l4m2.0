# import os
# import django

# os.environ.setdefault(
#     "DJANGO_SETTINGS_MODULE",
#     "l4m20.settings"
# )

# django.setup()

# from l4m_app.models import Real_calendar

import datetime
from zoneinfo import ZoneInfo

from icalendar import Calendar

from db_connector import DB_Connector
import requests


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

    print(uid, summary, dtstart)