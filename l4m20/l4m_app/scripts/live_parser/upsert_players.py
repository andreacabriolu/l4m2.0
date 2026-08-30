import io
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

import pandas as pd
import requests
import utilities as U
import math
from l4m_app.single_models import config, real_team, player

def _round(value):
    wage_multiplier = config.Config.objects.filter(Name="WageMultiplier").first()

    if wage_multiplier is not None:
        wage_multiplier = float(wage_multiplier.Value)
    else:
        wage_multiplier = 1.0  # Default value if not found in the database

    return math.floor((value * wage_multiplier) + 0.5) #round to nearest integer 

url = "https://apicdn.fantamaster.it/export/?format=excel&sort=name"

response = requests.get(url)
response.raise_for_status()  # Controlla se la richiesta ha avuto successo

df = pd.read_excel(io.BytesIO(response.content), sheet_name="Tutti", skiprows=1, skipfooter=2)

df = df.dropna(subset=["Nome"])

count_updated = 0
count_inserted = 0

realteams = real_team.RealTeam.objects.all()

players = player.Player.objects.all()
players.update(JustModified=False)  # Clean the JustModified flag for all players before the upsert operation

for _, row in df.iterrows():
    nome = U.clean_name(str(row["Nome"]).strip())
    squadra = str(row["Squadra"]).strip() if pd.notna(row["Squadra"]) else ""
    ruolo = str(row["Ruolo"]).strip() if pd.notna(row["Ruolo"]) else ""
    quotazione = int(_round(row["Quotazione"])) if pd.notna(row["Quotazione"]) else 0

    player.Player.objects.update_or_create(
        Surname=nome,
        defaults={
            "Role": ruolo,
            "RealTeam_id": realteams.filter(Name=squadra).first().id if realteams.filter(Name=squadra).exists() else None,
            "Status": "A",
            "Quotation": quotazione,
            "JustModified": True
        }
    )

# Imposta estero i giocatori non modificati dall'inserimento
player.Player.objects.filter(JustModified=False).update(Status='E')

print(f"Processati con successo {len(df)} giocatori nella tabella 'l4m_app_players'.")