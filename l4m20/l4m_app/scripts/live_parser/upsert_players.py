import io

import pandas as pd
import requests
import utilities as U

from db_connector import DB_Connector

# 1. Carica il file Excel
file_path = "live_parser/listone_26_27.xlsx"
url = "https://apicdn.fantamaster.it/export/?format=excel&sort=name"

# Saltiamo la prima riga di titolo dell'Excel per prendere la vera intestazione ('Surname', 'Squadra', 'Ruolo', ...)
# df = pd.read_excel(file_path, sheet_name="Tutti", skiprows=1)

response = requests.get(url)
response.raise_for_status()  # Controlla se la richiesta ha avuto successo

df = pd.read_excel(io.BytesIO(response.content), sheet_name="Tutti", skiprows=1, skipfooter=2)

# Rimuove eventuali righe vuote o senza Surname
df = df.dropna(subset=["Nome"])

# 2. Connessione al Database (sostituisci db.sqlite3 con il percorso del tuo DB o con la stringa di connessione)
conn = DB_Connector()

# 3. Query di Upsert (Inserisce se nuovo, aggiorna se il Surname esiste già)
count_updated = 0
count_inserted = 0

realteams_cache = dict(U.get_realteams(conn))

for _, row in df.iterrows():
    nome = U.clean_name(str(row["Nome"]).strip())
    squadra = str(row["Squadra"]).strip() if pd.notna(row["Squadra"]) else ""
    ruolo = str(row["Ruolo"]).strip() if pd.notna(row["Ruolo"]) else ""
    quotazione = int(row["Quotazione"]) if pd.notna(row["Quotazione"]) else 0

    conn.upsert_player(nome, ruolo, realteams_cache.get(squadra), quotazione)  # Inserisce il giocatore se non esiste già

# Salva le modifiche e chiudi
conn.commit()
conn.close()

print(f"Processati con successo {len(df)} giocatori nella tabella 'l4m_app_players'.")