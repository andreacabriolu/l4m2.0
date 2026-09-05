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
from l4m_app.single_models import config, real_team, player, quarantine

def _round(value):
    wage_multiplier = config.Config.objects.filter(Name="WageMultiplier").first()

    if wage_multiplier is not None:
        wage_multiplier = float(wage_multiplier.Value)
    else:
        wage_multiplier = 1.0  # Default value if not found in the database

    return math.floor((value * wage_multiplier) + 0.5) #round to nearest integer 

# url = "https://apicdn.fantamaster.it/export/?format=excel&sort=name"
filename = "l4m_app/scripts/live_parser/listone_26_27.xlsx"

# response = requests.get(url)
# response.raise_for_status()  # Controlla se la richiesta ha avuto successo

df = pd.read_excel(filename, sheet_name="Tutti", skiprows=1, skipfooter=2)
# df = pd.read_excel(io.BytesIO(response.content), sheet_name="Tutti", skiprows=1, skipfooter=2)

df = df.dropna(subset=["Nome"])

count_updated = 0
count_inserted = 0

# 1. Carica le squadre reali in un dizionario in memoria (evita query dentro il ciclo)
realteams_map = {rt.Name: rt.id for rt in real_team.RealTeam.objects.all()}

# 2. Carica tutti i player attuali in un dizionario per lookup rapido
existing_players = {p.Surname: p for p in player.Player.objects.all()}

updated_players = []
created_players = []
processed_ids = set()

# Prepara le liste per la Quarantena
q_player_ids = set(quarantine.Quarantine.objects.values_list('Player_id', flat=True))

for _, row in df.iterrows():
    nome = U.clean_name(str(row["Nome"]).strip())
    squadra = str(row["Squadra"]).strip() if pd.notna(row["Squadra"]) else ""
    ruolo = str(row["Ruolo"]).strip() if pd.notna(row["Ruolo"]) else ""
    quotazione = int(_round(row["Quotazione"])) if pd.notna(row["Quotazione"]) else 0
    
    team_id = realteams_map.get(squadra)

    if nome in existing_players:
        p = existing_players[nome]
        processed_ids.add(p.id)
        
        new_status = 'Q' if p.id in q_player_ids else 'A'
        
        # AGGIORNA IN MEMORIA LE QUOTAZIONI    
        p.InitialQuotation = quotazione            
        p.Quotation = quotazione
        p.Status = new_status
        updated_players.append(p)

# 4. Esegui le operazioni sul DB in BULK (uniche 2 query veloci!)
if created_players:
    player.Player.objects.bulk_create(created_players)

if updated_players:
    player.Player.objects.bulk_update(
        updated_players, 
        fields=['Role', 'RealTeam_id', 'InitialQuotation', 'Status', 'Quotation', 'JustModified']
    )

print(f"Processati con successo {len(df)} giocatori nella tabella 'l4m_app_players'.")
print(f"Giocatori aggiornati: {len(updated_players)}")
print(f"Giocatori inseriti: {len(created_players)}")