import psycopg2
import datetime
from collections import defaultdict

# REMOTE
conn = psycopg2.connect(
     dbname="l4m20_db",
     user="",
     password="",
     host="127.0.0.1",
     #host="209.38.103.87",
     port="5432"
)
cur = conn.cursor()

def round_robin_schedule(teams):
    """Generate a round robin schedule for an even number of teams (IDs)."""
    if len(teams) % 2:
        teams.append('BYE')  # If odd number of teams
    
    n = len(teams)
    schedule = []

    teams = teams[:]  # copy

    for round_num in range(n - 1):
        pairs = []
        for i in range(n // 2):
            t1 = teams[i]
            t2 = teams[n - 1 - i]
            if t1 != 'BYE' and t2 != 'BYE':
                pairs.append((t1, t2))
        schedule.append(pairs)
        # Rotate teams but keep first team fixed
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    
    return schedule

# get mapping id -> name
cur.execute('SELECT id, "Name" FROM "l4m_app_team";')
id_to_name = {tid: name for tid, name in cur.fetchall()}

# get series memberships (only IDs here)
cur.execute('SELECT team_id, series_id FROM "l4m_app_team_Series";')
rows = cur.fetchall()

series_groups = defaultdict(list)
for team_id, series_id in rows:
    series_groups[series_id].append(team_id)


# ---------------------------------------------------------------------- PRINT QUERIES
# Print results
for series_id, teams in series_groups.items():
    print(f"series_{series_id} = {teams}")  # still IDs
    match_days = round_robin_schedule(teams)
    for day_num, matches in enumerate(match_days, 1):
        print(f"Match Day {day_num}:")
        for t1, t2 in matches:
            name1 = id_to_name.get(t1, str(t1))
            name2 = id_to_name.get(t2, str(t2))
            print(f"  {name1} vs {name2}")
        print()
        output_file = "matches_inserts.sql"
insert_statements = []

# --- Part 1: CompetitionCalendar inserts (35 days) ---
for day in range(1, 36):
    stmt = (
        f'INSERT INTO "l4m_app_competition_calendar" '
        f'("Competition_id", "Day", "Stage", "HomeAway", "Overtime", "Penalties") '
        f"VALUES (1, {day}, 'Girone', false, false, false);"
    )
    insert_statements.append(stmt)

cur.execute('SELECT id, "Name" FROM "l4m_app_team";')
rows = cur.fetchall()
team_names = {team_id: name for team_id, name in rows}

# --- Part 2: MatchesCalendar inserts (repeat 5 times) ---
for series_id, teams in series_groups.items():
    match_days = round_robin_schedule(teams)  # 7 matchdays
    for repeat in range(5):  # repeat 5 times
        for day_offset, matches in enumerate(match_days):
            day_num = day_offset + 1 + repeat * len(match_days)  # 1..35
            for t1, t2 in matches:
                t1_name = team_names[t1]
                t2_name = team_names[t2]
                stmt = (
                    f'INSERT INTO "l4m_app_matches_calendar" '
                    f'("CompetitionCalendar_id", "HomeTeam_id", "AwayTeam_id") '
                    f'VALUES ({day_num}, {t1}, {t2});'
                    f'  -- {t1_name} vs {t2_name} day {day_num}'
                )
                insert_statements.append(stmt)

# --- Write to file ---
with open(output_file, "w") as f:
    for stmt in insert_statements:
        f.write(stmt + "\n")

print(f"✅ Written {len(insert_statements)} INSERTs to {output_file}")

cur.close()
conn.close()
