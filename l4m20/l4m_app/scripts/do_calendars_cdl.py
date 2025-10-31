import psycopg2
import datetime
from collections import defaultdict
import random
from decouple import config

conn = psycopg2.connect(
     dbname=config('DB_NAME'),
     user=config('DB_USER'),
     password=config('DB_PASSWORD'),
     host="127.0.0.1",
     #host="209.38.103.87",
     port="5432"
)
cur = conn.cursor()

def round_robin_schedule(teams):
    """
    Generate a full round robin schedule (home and away) 
    for an even number of teams (IDs).
    
    This version keeps the "first half" and "second half" 
    separate, but alternates the fixed team's home/away
    status in the first half to prevent streaks.
    """
    if len(teams) % 2:
        teams.append('BYE')  # If odd number of teams
    
    n = len(teams)
    first_half = []
    
    rotating_teams = teams[:] 

    for round_num in range(n - 1):
        pairs = []
        for i in range(n // 2):
            t1 = rotating_teams[i]
            t2 = rotating_teams[n - 1 - i]
            
            # --- This is the new logic ---
            # For the fixed team (i=0), alternate home/away
            # In odd-numbered rounds, swap the pair
            if i == 0 and round_num % 2:
                # If it's an odd round, swap the fixed team to away
                if t1 != 'BYE' and t2 != 'BYE':
                    pairs.append((t2, t1))
            else:
                # Even round, or not the fixed team
                if t1 != 'BYE' and t2 != 'BYE':
                    pairs.append((t1, t2))
            # --- End new logic ---
                
        first_half.append(pairs)
        
        # Rotate
        rotating_teams = [rotating_teams[0]] + [rotating_teams[-1]] + rotating_teams[1:-1]
    
    # Create the second half by swapping
    second_half = []
    for round_matches in first_half:
        return_round = []
        for (t1, t2) in round_matches:
            return_round.append((t2, t1))
        second_half.append(return_round)

    # Return the full schedule, first half then second half
    return first_half + second_half
    
# get mapping id -> name
cur.execute('SELECT id, "Name" FROM "l4m_app_team";')
id_to_name = {tid: name for tid, name in cur.fetchall()}

# ~ # Switch it on only to make gironi
# ~ ids = list(id_to_name.keys())
# ~ random.shuffle(ids)
# ~ print('insert into "l4m_app_team_Series" (team_id,series_id) values')
# ~ cnt=0
# ~ gir=15
# ~ for ii in ids:
    # ~ cnt=cnt+1
    # ~ print('(',ii,',',gir,'),')
    # ~ gir=15 + cnt//4  

# get series memberships (only IDs here)
cur.execute('SELECT team_id, series_id FROM "l4m_app_team_Series" where series_id>14;')
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
for day in range(10, 22, 2):
    stmt = (
        f'INSERT INTO "l4m_app_competition_calendar" '
        f'("Competition_id", "Day", "Stage", "HomeAway", "Overtime", "Penalties") '
        f"VALUES (2, {day}, 'Girone', true, false, false);"
    )
    #insert_statements.append(stmt)

cur.execute('SELECT id, "Name" FROM "l4m_app_team";')
rows = cur.fetchall()
team_names = {team_id: name for team_id, name in rows}

# --- Part 2: MatchesCalendar inserts (repeat 5 times) ---
for series_id, teams in series_groups.items():
    match_days = round_robin_schedule(teams)  # 7 matchdays
    #for repeat in range(1):  # repeat 5 times
    for day_offset, matches in enumerate(match_days):
            day_num = day_offset + 42 
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

print(f"✅ Written {len(insert_statements)} INSERTs")
# to {output_file}")

cur.close()
conn.close()
