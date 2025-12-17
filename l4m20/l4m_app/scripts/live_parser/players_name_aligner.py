import csv
import json
import requests as req
import constants as C
import utilities as U
from db_connector import *

TEST = False

if(not TEST):
    url = "https://publicapi.fantamaster.it/livescores/?tcache=1756165942189"
    resp = req.get(url)
    resp_content = resp.content

    resp_json = json.loads(resp_content)
else:
    f = open('live_parser/fake.json','r')
    resp_json = json.loads(f.read())
    f.close()

players_csv_path = "live_parser/all_players.csv"

try:
    conn = DB_Connector()
    players_csv = U.read_csv(players_csv_path)
    players_db = dict(U.get_players(conn))

    report = U.report_players_name_alignment(players_csv, players_db)
    
    report['wrong'] = []
    # Manually manage known exceptions
    report['wrong'].append(('Amin_Sarr', 'Verona', 'A'))
    report['wrong'].append(('Danilo_Veiga', 'Lecce', 'D'))
    report['wrong'].append(('Di_Gennaro_R', 'Inter', 'P'))
    report['wrong'].append(('Lucumi', 'Bologna', 'D'))
    report['wrong'].append(('Montipo', 'Verona', 'P'))
    report['wrong'].append(('Van_der_Brempt', 'Como', 'D'))

    with open('live_parser/players_name_alignment_report_fixed.csv', 'w') as report_file_fixed:
        csv.writer(report_file_fixed).writerows([['Player_Name_CSV', 'Team_CSV', 'Role_CSV', 'Player_Name_DB']])
        for row in report['aligned']:
            csv.writer(report_file_fixed).writerows([row])
        csv.writer(report_file_fixed).writerows([['----------------------------WRONG-----------------------------------']])
        for row in report['wrong']:
            csv.writer(report_file_fixed).writerows([row])
        csv.writer(report_file_fixed).writerows([['---------------------------NOT ALIGNED------------------------------------']])
        for row in report['not_aligned']:
            csv.writer(report_file_fixed).writerows([row])
        csv.writer(report_file_fixed).writerows([['---------------------------DB------------------------------------']])
        for row in players_db.items():
            csv.writer(report_file_fixed).writerows([[row[0], row[1], '']])

    realteams_cache = dict(U.get_realteams(conn))
    
    for player_name_csv, team_csv, role_csv, unknown_id in report['not_aligned']:
        conn.insert_player(player_name_csv, role_csv, realteams_cache.get(team_csv))
    conn.commit()

except Exception as e:
        print(f"Error aligning player names: {e}")