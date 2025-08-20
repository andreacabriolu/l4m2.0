import csv
import psycopg2

CSV_FILE = "01.csv"
DAY = 1   # giornata
COMPETITION_ID = 1  # id del campionato (da modificare se serve)

def main():
    # REMOTE
    conn = psycopg2.connect(
         dbname="l4m20_db",
         user="giamba",
         password="",
         host="127.0.0.1",
         #host="209.38.103.87",
         port="5432"
    )
    cur = conn.cursor()

    current_team = None

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)

        for row in reader:
            if not row or len(row) < 4:
                continue

            # Rileva intestazioni di squadra
            if row[0] and row[1] == "" and "Cod." not in row[0]:
                current_team = row[0].strip()
                continue

            # Salta intestazioni colonne
            if row[0] == "Cod.":
                continue

            try:
                code, role, surname, voto, gf, gs, rp, rs, rf, au, amm, esp, ass = row[:13]
            except ValueError:
                continue

            surname = surname.strip()
            surname = surname.replace(" ", "_").replace(".","").replace("e'","è")

            # Trova Player_id
            cur.execute('SELECT id FROM l4m_app_player WHERE "Surname" = %s', (surname,))
            player_row = cur.fetchone()
            if not player_row:
                print(f"⚠️ Giocatore non trovato: {surname}")
                continue
            player_id = player_row[0]

            # Trova RealTeam_id
            cur.execute('SELECT id FROM l4m_app_realteam WHERE "Name" = %s', (current_team,))
            team_row = cur.fetchone()
            if not team_row:
                print(f"⚠️ Squadra non trovata: {current_team}")
                continue
            realteam_id = team_row[0]

            # Costruisci valori
            data = {
                "Day": DAY,
                "Vote": float(voto.replace("*", "")) if voto else None,
                "GoalSc": int(gf or 0),
                "GoalTa": int(gs or 0),
                "GoalDe": int(0),
                "PenSa": int(rp or 0),
                "PenSc": int(rs or 0),
                "PenMi": int(rf or 0),
                "Own": int(au or 0),
                "Yel": int(amm or 0),
                "Red": int(esp or 0),
                "AssS": int(ass or 0),
                "AssH": 0,
                "AssL": 0,
                "AssP": 0,
                "SubJ": 0,
                "Sub": 0,
                "Competition_id": COMPETITION_ID,
                "Player_id": player_id,
                "RealTeam_id": realteam_id,
            }

            # Inserisci
            query = """
                INSERT INTO l4m_app_vote
                ("Day", "Vote", "GoalSc", "GoalTa","GoalDe", "PenSc", "PenMi", "PenSa", "Own", "Yel", "Red",
                 "AssS", "AssH", "AssL", "AssP", "SubJ", "Sub", "Competition_id", "Player_id", "RealTeam_id")
                VALUES (%(Day)s, %(Vote)s, %(GoalSc)s, %(GoalTa)s, %(GoalDe)s, %(PenSc)s, %(PenMi)s, %(PenSa)s,
                        %(Own)s, %(Yel)s, %(Red)s, %(AssS)s, %(AssH)s, %(AssL)s, %(AssP)s,
                        %(SubJ)s, %(Sub)s, %(Competition_id)s, %(Player_id)s, %(RealTeam_id)s)
            """
            print(cur.mogrify(query, data).decode("utf-8"))  # 👈 stampa la query completa
            print(f"✅ Inserito voto per {surname} ({current_team})")
            cur.execute(query,data)

    #conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
