import csv
import constants as C
from db_connector import *
from vote_live import *
from l4m_app.single_models import competition_calendar, player, vote, real_team, season, real_calendar


def get_current_season(conn:DB_Connector):
    try:
        rows = conn.select(table="l4m_app_season", cols='\"id\"', conditions='"Active"=%s', data=('true',))
        if len(rows) <= 0:
            return None
        return rows[0][0]
    except Exception as e:
        raise e

def get_today_competitions(conn:DB_Connector, current_day, current_season):
    try:
        rows = conn.select(table="l4m_app_competition_calendar", 
                           cols='\"Competition_id\"', 
                           conditions='"Day"=%s AND "Season_id"=%s', 
                           data=(current_day, current_season))
        competitions = set()
        for row in rows:
            competitions.add(row[0])
        return competitions
    except Exception as e:
        raise e

def set_final(score, real_teams, current_day, current_season):
    if score['time'] == C.Events.END_MATCH:
        team_home = real_teams.filter(Name=score['home_name']).first()
        team_away = real_teams.filter(Name=score['away_name']).first()
        if team_home is None or team_away is None:
            return

        real_calendar.Real_calendar.objects.filter(
            Day=current_day, 
            RealTeamHome_id=team_home, 
            RealTeamAway_id=team_away, 
            Season_id=current_season).update(FT=True)

        # conn.update(table="l4m_app_real_calendar", set='"FT"=true', 
        #             conditions='"Day"=%s AND "RealTeamHome_id"=%s AND "RealTeamAway_id"=%s AND "Season_id"=%s', 
        #             data=(current_day, team_home, team_away, current_season))
        # pass

def report_old_players_missing_from_csv(players_db, players_csv):
    missing_players = []
    for player_name_db in players_db:
        if player_name_db[0] not in players_csv:
            missing_players.append(player_name_db)
    return missing_players

def calculate_totvote(v):
    sum = v.Vote
    
    sum += \
    (v.AssP * C.Scores.PENALTY_PROCURED) + \
    (v.AssS * C.Scores.ASS_STD) + \
    (v.GoalTa * C.Scores.GOAL_TAKEN) + \
    (v.GoalSc * C.Scores.GOAL) + \
    (v.Own * C.Scores.OWN_GOAL) + \
    (v.PenMi * C.Scores.PENALTY_MISSED) + \
    (v.PenSa * C.Scores.PENALTY_SAVED) + \
    (v.PenSc * C.Scores.PENALTY_SCORED) + \
    (v.Red * C.Scores.RED) + \
    (v.YelRed * C.Scores.RED) + \
    (v.Yel * C.Scores.YELLOW)  

    return sum

def report_players_name_alignment(players_csv, players_db):
    report = {
        'aligned': [],
        'not_aligned': []
    }

    for player_name_csv, (team_csv, role_csv) in players_csv.items():
        if player_name_csv in players_db:
            report['aligned'].append((player_name_csv, team_csv, role_csv, players_db[player_name_csv]))
        else:
            report['not_aligned'].append((player_name_csv, team_csv, role_csv, None))
    
    return report

def read_csv(path):
    players = {}
    try:
        with open(path, mode='r', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip header
            for row in csvreader:
                if len(row) < 2:
                    continue
                surname = clean_name(row[0].strip())
                playerteam = row[1].strip()
                playerrole = row[2].strip()
                players[surname] = (playerteam, playerrole)
    except Exception as e:
        print(f"Error reading CSV file {path}: {e}")
        
    return players

def clean_name(name):
    return name.replace(' ','_').replace('\'','')

def set_live(score, votes, players):
    hlineup = score['home_lineups']
    hbench = score['home_bench']
    alineup = score['away_lineups']
    abench = score['away_bench']

    for hl in hlineup:
        hl = clean_name(hl)
        pl = players.filter(Surname=hl).first()
        if pl is None:
            continue
        # if hl not in players:
        #     continue
        pl_id = pl.id
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for hp in hbench:
        hp = clean_name(hp)
        pl = players.filter(Surname=hp).first()
        if pl is None:
            continue
        # if hp not in players:
        #     continue
        pl_id = pl.id
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for al in alineup:
        al = clean_name(al)
        pl = players.filter(Surname=al).first()
        if pl is None:
            continue
        pl_id = pl.id
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

    for ap in abench:
        ap = clean_name(ap)
        pl = players.filter(Surname=ap).first()
        if pl is None:
            continue
        pl_id = pl.id
        if(pl_id not in votes):
            continue
        vote = votes[pl_id]
        vote.Live = True

def make_vote_for_player(pl, votes, real_teams):
    # vote = Vote_Live_Obj()
    _vote = vote.Vote()
    _vote.Player = pl
    _vote.Vote = 0.0
    _vote.TotVote = 0.0
    _vote.GoalSc = 0
    _vote.GoalTa = 0
    _vote.PenSc = 0
    _vote.PenMi = 0
    _vote.PenSa = 0
    _vote.Own = 0
    _vote.Yel = 0
    _vote.Red = 0
    _vote.YelRed = 0
    _vote.AssS = 0
    _vote.AssP = 0
    _vote.Live = False
    _vote.Sub = 0
    _vote.RealTeam = real_teams.filter(id=pl.RealTeam_id).first()

    votes.append(_vote)

def fill_with_events(events, players, votes, real_teams):

    players_id_set = set()
    for pl_id, vote in votes.items():
        players_id_set.add(pl_id)

    for event in events:

        pl_name = event.get('player', None)
        in_player_name = event.get('in', None)
        out_player_name = event.get('out', None)

        if pl_name is not None:
            pl_name = clean_name(pl_name)
            pl_obj = players.filter(Surname=pl_name).first()
            if pl_obj is None:
                continue
            pl_id = pl_obj.id
            if pl_id not in players_id_set:
                make_vote_for_player(pl_obj, votes, real_teams)
            # if pl_id not in votes:
            #     make_vote_for_player(pl_obj, votes, real_teams)

        #SHOULD NOT HAPPEN, BUT JUST IN CASE
        # if 'player' in event and clean_name(event['player']) not in players:
        #     continue
        # if 'in' in event and clean_name(event['in']) not in players:
        #     continue
        # if 'out' in event and clean_name(event['out']) not in players:
        #     continue
        # if 'in' in event and clean_name(event['in']) not in players:
        #     continue
        # if 'out' in event and clean_name(event['out']) not in players:
        #     continue
        # if 'details' in event and event['details'] != '' and clean_name(event['details']) not in players:
        #     continue
        
        _type = event['type']
        match _type:
            case C.Events.YELLOW_CARD:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                # if pl_id not in votes:
                #     make_vote_for_player(pl_id, votes, players_realteam)

                vote = votes[pl_id]
                vote.Yel = 1
            case C.Events.RED_CARD:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                # if pl_id not in votes:
                #     make_vote_for_player(pl_id, votes, players_realteam)

                vote = votes[pl_id]
                vote.Red = 1
                vote.Yel = 0

            case C.Events.YELLOW_RED_CARD:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                # if pl_id not in votes:
                #     make_vote_for_player(pl_id, votes, players_realteam)

                vote = votes[pl_id]
                vote.YelRed = 1
                vote.Yel = 0

            case C.Events.GOAL:
                if 'details' in event and event['details'] != '' and players.filter(Surname=clean_name(event['details'])).exists():
                    pl_assist_id = players.filter(Surname=clean_name(event['details'])).first().id
                    vote = votes[pl_assist_id]
                    vote.AssS = vote.AssS + 1

                vote = votes[pl_id]
                vote.GoalSc = vote.GoalSc + 1

            case C.Events.GOAL_TAKEN:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                vote = votes[pl_id]
                vote.GoalTa = vote.GoalTa + 1

            case C.Events.OWN_GOAL:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                vote = votes[pl_id]
                vote.Own = vote.Own + 1

            case C.Events.PENALTY_SCORED:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                vote = votes[pl_id]
                vote.PenSc = vote.PenSc + 1

            case C.Events.PENALTY_MISSED:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                vote = votes[pl_id]
                vote.PenMi = vote.PenMi + 1

            case C.Events.PENALTY_SAVED:
                # pl_id = players[clean_name(event['player'])]
                # if pl_id is None:
                #     continue

                vote = votes[pl_id]
                vote.PenSa = vote.PenSa + 1

            case C.Events.SUB:
                continue

def delete_votes_of_day(conn:DB_Connector, day, season):
    if day == "":
        return
    
    try:
        conn.delete("l4m_app_vote", conditions=f"\"Day\"={day} AND \"Season_id\"={season}")
    except Exception as e:
        raise e

def insert_votes(conn:DB_Connector, votes, today_competitions=None):
    try:
        for _,vote in votes.items():
            if vote.Live:
                continue
            for comp in today_competitions:
                data_vote = (vote.Day, 
                            vote.Vote, 
                            vote.TotVote,
                            vote.GoalSc, 
                            vote.GoalTa, 
                            0, #GoalDe 
                            vote.PenSc, 
                            vote.PenMi,
                            vote.PenSa,
                            vote.Own, 
                            vote.Yel, 
                            vote.Red, 
                            vote.YelRed, 
                            vote.AssS,
                            0, #vote.AssH,
                            0, #vote.AssL,
                            vote.AssP,
                            0, #vote.SubJ,
                            vote.Sub, 
                            comp, #one vote per competition
                            vote.Player,
                            vote.RealTeam,
                            vote.Live,
                            vote.Season)
                conn.insert(table="l4m_app_vote", data=data_vote)
    except Exception as e:
        raise e
    
def get_players_realteam(conn:DB_Connector):
    try:
        return conn.select_all(table="l4m_app_player", cols='\"id\",\"RealTeam_id\"')
    except Exception as e:
        raise e

def get_all_active_players(conn:DB_Connector):
    try:
        return conn.select(table="l4m_app_player", cols='\"Surname\",\"Role\",\"id\"', conditions='"Status"=%s', data='A')
    except Exception as e:
        raise e    

def get_all_players(conn:DB_Connector):
    try:
        return conn.select_all(table="l4m_app_player", cols='\"Surname\",\"Role\",\"id\"')
    except Exception as e:
        raise e    

def get_players(conn:DB_Connector):
    try:
        return conn.select_all(table="l4m_app_player", cols='\"Surname\",\"id\"')
    except Exception as e:
        raise e
    
def get_current_assp(_vote):
    try:
        n_assp = vote.Vote.objects.filter(Day=_vote.Day, Player=_vote.Player, Season=_vote.Season).values_list('AssP', flat=True).first()
        if n_assp is None:
            return 0
        
        return n_assp

        # rows = conn.select(table="l4m_app_vote", 
        #                    cols='\"AssP\"', 
        #                    conditions='"Day"=%s and "Player_id"=%s and "Season_id"=%s', 
        #                    data=(vote.Day, vote.Player, vote.Season))
        # if len(rows) <= 0:
        #     return 0
        # return rows[0][0]

    except Exception as e:
        raise e
    
def get_realteams(conn:DB_Connector):
    try:
        return conn.select(table="l4m_app_realteam", cols='\"Name\",\"id\"', conditions='"Status"=%s', data=('A',))
    except Exception as e:
        raise e