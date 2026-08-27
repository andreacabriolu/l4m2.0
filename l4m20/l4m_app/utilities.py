from .models import *
from django.db.models import Q, Sum, Count, Case, When, Value, F, OuterRef, Subquery, Exists
import json
import datetime
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from zoneinfo import ZoneInfo
from l4m20 import constants as C
import requests as req
from .libs import *

def get_signed_contracts(teamid):
    _squads = squads.Squads.objects.filter(
        Q(Team_id=teamid) & 
        Q(Season_id=get_current_season().id)).values('Player_id','Years')
    
    signed_contracts_per_role = {
        'P': {'1': 0, '2': 0, '3': 0},
        'D': {'1': 0, '2': 0, '3': 0},
        'C': {'1': 0, '2': 0, '3': 0},
        'A': {'1': 0, '2': 0, '3': 0}
    }

    for s in _squads:
        p = get_object_or_404(player.Player, pk=s['Player_id'])
        if s['Years'] in [1, 2, 3]: #avoid not signed contracts
            signed_contracts_per_role[p.Role][str(s['Years'])] += 1

    return signed_contracts_per_role

def get_bids_history(market):
    history = bet_history.Bet_History.objects.filter(Q(Market_id=market)).values(
        'id','Player_id','Amount','Time','Carognata','Team_id').order_by('-Time')

    bids_history = []
    #group by player and get the last bid for each player
    
    for player_id in set([b['Player_id'] for b in history]):
        last_bids = history.filter(Player_id=player_id).order_by('-Time')
        p = get_object_or_404(player.Player, pk=player_id)

        bids_history.append({
            'player_name': f"{p.Surname}",
            'player_id': p.id,
            'bids' : [{
                'amount': b['Amount'],
                'time': b['Time'].astimezone(ZoneInfo('Europe/Rome')).strftime("%Y-%m-%d %H:%M:%S"),
                'carognata': b['Carognata'],
                'teamname': get_team_name_by_id(b['Team_id'])
            } for b in last_bids]

        })

    return bids_history

def undo_bet(data, team):
    logger.debug(f"UNDOING BET: {data['bet_id']} FOR TEAM: {team['id']} AND PLAYER: {data['player_id']}")

    teamid = team['id']
    
    #check for existing bet
    existing_bet = bet.Bet.objects.filter(Q(id=data['bet_id']) & Q(Team_id=teamid)).first()
    if not existing_bet:
        return C.CancelBidResult.CANCEL_NOT_FOUND
    
    existing_bet_time = existing_bet.Time

    #check if a new bet has been placed for the same player after the bet to be undone
    overcome_bet_exists = bet.Bet.objects.filter(
        Q(Player_id=data['player_id']) &
        Q(Session_id=existing_bet.Session_id) &
        Q(Time__gt=existing_bet_time)
    ).exists()

    if overcome_bet_exists:
        return C.CancelBidResult.CANCEL_BET_OVERCOME

    #check if the bet is still within the cancel timeout
    time_since_bet = datetime.datetime.now(ZoneInfo('Europe/Rome')) - existing_bet.Time
    if time_since_bet.total_seconds() > C.BID_CANCEL_TIMEOUT:
        return C.CancelBidResult.CANCEL_EXPIRED

    existing_bet.delete()

    #restore old bet, if existing
    last_bet = bet_history.Bet_History.objects.filter(
        Player_id=data['player_id'], 
        Session_id=get_current_session(existing_bet.Market).id).order_by('-Time').first()
    
    if last_bet:
        old_bet = bet.Bet(
            Amount=last_bet.Amount,
            Ghost=last_bet.Ghost,
            Carognata=last_bet.Carognata,
            Player_id=last_bet.Player_id,
            Team_id=last_bet.Team_id,
            Session_id=last_bet.Session_id,
            Time=last_bet.Time,
            Market_id=last_bet.Market_id,
            Expiration_Date=last_bet.Expiration_Date
        )
        old_bet.save()

    return C.CancelBidResult.CANCEL_OK

def get_current_season():
    return season.Season.objects.filter(Active=True).first()

def parse_ranking_line(ranking_line):
    json_l = json.loads(ranking_line)
    lines = []
    
    for l in json_l:
        line = {}
        for k,v in l.items():
            line['team'] = team.Team.objects.get(pk=k).Name.upper()
            for _k,_v in v.items():
                line[_k] = float(_v)

        lines.append(line)
    
    #sort by pt and then by fpt
    lines.sort(key=lambda x: (x.get('pt', 0), x.get('fpt', 0)), reverse=True)

    return lines

def get_current_stage(competition_id):
    current_day = get_current_day(competition_id)
    cc = competition_calendar.CompetitionCalendar.objects.filter(Q(Competition=competition_id) & Q(Day=current_day)).values('Stage')
    return cc.first()['Stage'] if len(cc) > 0 else None

def get_layer_name_by_matches_count(matches_count):
    match matches_count:
        case 32:
            return 'Trentaduesimi'
        case 16:
            return 'Sedicesimi'
        case 8:
            return 'Ottavi'
        case 4:
            return 'Quarti'
        case 2:
            return 'Semifinali'
        case 1:
            return 'Finale'
        case _:
            return f'round_of_{matches_count*2}'
        
def get_matches_results_for_bracket(calendar_id):
    return list(matches_results.MatchesResults.objects.\
                        filter(MatchesCalendar__CompetitionCalendar_id=calendar_id).\
                        values('MatchesCalendar_id',
                            'Team_id',
                            'NGoals',
                            'ExtraTimePlayers',
                            'FpO',
                            'Pen',
                            'AggregateScore',
                            'ET_Winner',
                            'Pen_Winner',
                            'Winner',
                            'MatchesCalendar__HomeTeam_id',
                            'MatchesCalendar__AwayTeam_id',
                            'MatchesCalendar__CompetitionCalendar__Overtime'))

def get_winner(home_data, away_data):
    if home_data['ngoals'] > away_data['ngoals']:
        return (True, False)
    elif away_data['ngoals'] > home_data['ngoals']:
        return (False, True)
    elif home_data['ngoals'] == away_data['ngoals']:
        if home_data['et_winner']:
            return (True, False)
        elif away_data['et_winner']:
            return (False, True)
        elif home_data['pen_winner']:
            return (True, False)
        elif away_data['pen_winner']:
            return (False, True)
        
    return (False, False) #DRAW, IMPOSSIBLE TO DECIDE WINNER

def get_all_final_stages(competition_id):
    return competition_calendar.CompetitionCalendar.objects.filter(Q(Competition=competition_id) &\
                ~Q(Stage='Girone')).values('Stage','id','Overtime','Num_Matches').distinct()

def get_et_outcome(home_data, away_data):
    if home_data is None or away_data is None:
        return False
    return home_data['ET_Winner'] or away_data['ET_Winner'] and not (home_data['Pen_Winner'] or away_data['Pen_Winner'])

def get_pen_outcome(home_data, away_data):
    if home_data is None or away_data is None:
        return False
    return home_data['Pen_Winner'] or away_data['Pen_Winner']

def get_bracket_data_for_competition(competition_id):
    bracket_data = []
    final_calendars = list(get_all_final_stages(competition_id).order_by('Num_Matches').reverse())
    grouped_calendars = {}
    for fc in final_calendars:
        layer_name = get_layer_name_by_matches_count(fc['Num_Matches'])
        if layer_name not in grouped_calendars:
            grouped_calendars[layer_name] = []
        grouped_calendars[layer_name].append(fc)

    layer_results = {}

    for layer_name, gc in grouped_calendars.items(): # loop layers (ottavi, quarti...)

        if layer_name not in layer_results:
                layer_results[layer_name] = []

        if len(gc) == 2: # legs
            first_leg, second_leg = gc[0], gc[1]

            results_first_leg = get_matches_results_for_bracket(first_leg['id'])
            results_second_leg = get_matches_results_for_bracket(second_leg['id'])
            
            grouped_results_first_leg = {}
            for result in results_first_leg:
                mc_id = result['MatchesCalendar_id']
                if mc_id not in grouped_results_first_leg:
                    grouped_results_first_leg[mc_id] = []
                grouped_results_first_leg[mc_id].append(result)
            
            grouped_results_second_leg = {}
            for result in results_second_leg:
                mc_id = result['MatchesCalendar_id']
                if mc_id not in grouped_results_second_leg:
                    grouped_results_second_leg[mc_id] = []
                grouped_results_second_leg[mc_id].append(result)

            results_coupled_by_legs = {}
            for results_first_leg in grouped_results_first_leg.values(): #results available for first leg
                team_home = results_first_leg[0]['MatchesCalendar__HomeTeam_id']
                team_away = results_first_leg[0]['MatchesCalendar__AwayTeam_id']
                results_coupled_by_legs[(team_home, team_away)] = (results_first_leg, None) #initialize with first leg results and None for second leg

            for results_second_leg in grouped_results_second_leg.values(): #results available for second leg
                team_home = results_second_leg[0]['MatchesCalendar__HomeTeam_id']
                team_away = results_second_leg[0]['MatchesCalendar__AwayTeam_id']
                if (team_away, team_home) in results_coupled_by_legs: #check if the second leg teams are the opposite of the first leg teams
                    results_coupled_by_legs[(team_away, team_home)] = (results_coupled_by_legs[(team_away, team_home)][0], results_second_leg) #update the second leg results

            if len(results_coupled_by_legs) == 0: #no results available for both legs
                for i in range(gc[0]['Num_Matches']): #initialize empty results for the number of matches in the layer
                    layer_results[layer_name].append({
                        'home': '-',
                        'away': '-',
                        "is_final": False,
                        "legs" : [
                            {                    
                                'home_score': '-' ,
                                'away_score': '-' ,
                                'played': False
                            },
                            {                    
                                'home_score': '-' ,
                                'away_score': '-' ,
                                'played': False
                            },
                        ], 
                        "aggregate_home": '-',
                        "aggregate_away": '-',
                        "winner": None
                    })

                continue

            for leg_result in results_coupled_by_legs.values():
                leg_result[0].sort(key= lambda x: x['MatchesCalendar__HomeTeam_id'] == x['Team_id'], reverse=True) #sort first leg results to have home team first
                leg_result[1].sort(key=lambda x: x['MatchesCalendar__HomeTeam_id'] == x['Team_id'], reverse=True) if leg_result[1] else None #sort second leg results to have home team first
                result_home_first_leg, result_away_first_leg = leg_result[0][0], leg_result[0][1]
                result_home_second_leg, result_away_second_leg = leg_result[1][0] if leg_result[1] else None, leg_result[1][1] if leg_result[1] else None
            
                layer_results[layer_name].append({
                    'home': get_team_name_by_id(result_home_first_leg['Team_id']),
                    'away': get_team_name_by_id(result_away_first_leg['Team_id']),
                    "is_final": False,
                    "legs" : [
                        {                    
                            'home_score': result_home_first_leg['NGoals'] ,
                            'away_score': result_away_first_leg['NGoals'] ,
                            'played': True
                        },
                        {                    
                            'home_score': result_away_second_leg['NGoals'] if result_away_second_leg is not None else '-',
                            'away_score': result_home_second_leg['NGoals'] if result_home_second_leg is not None else '-',
                            'played': True if result_home_second_leg is not None and result_away_second_leg is not None else False,
                            "et": get_et_outcome(result_home_second_leg, result_away_second_leg),
                            "pen": get_pen_outcome(result_home_second_leg, result_away_second_leg),
                            "penalties": {
                                "home_penalties": result_away_second_leg['Pen'] if result_away_second_leg is not None else 0,
                                "away_penalties": result_home_second_leg['Pen'] if result_home_second_leg is not None else 0
                            }
                        },
                    ], 
                    "aggregate_home": result_home_first_leg['NGoals'] + (result_away_second_leg['NGoals'] if result_away_second_leg is not None else 0),
                    "aggregate_away": result_away_first_leg['NGoals'] + (result_home_second_leg['NGoals'] if result_home_second_leg is not None else 0),
                    "winner": None
                })
        else: # FINAL
            result_final = get_matches_results_for_bracket(gc[0]['id'])
            grouped_results_final = {}
            for result in result_final:
                mc_id = result['MatchesCalendar_id']
                if mc_id not in grouped_results_final:
                    grouped_results_final[mc_id] = []
                grouped_results_final[mc_id].append(result)

            result_home = None
            result_away = None
            for results in grouped_results_final.values():
                result_home, result_away = results[0], results[1]

            layer_results[layer_name].append({
                        'home': get_team_name_by_id(result_home['Team_id']) if result_home is not None else "-",
                        'away': get_team_name_by_id(result_away['Team_id']) if result_away is not None else "-",
                        "is_final": True,
                        "home_score": result_home['NGoals'] if result_home is not None else '-' ,
                        "away_score": result_away['NGoals'] if result_away is not None else '-' ,
                        "et": get_et_outcome(result_home, result_away),
                        "pen": get_pen_outcome(result_home, result_away),
                        "penalties": {
                            "home_penalties": result_home  ['Pen'] if result_home is not None else 0,
                            "away_penalties": result_away['Pen'] if result_away is not None else 0
                        },
                        "winner": None
                    })
            
    #update winners
    for _,v in layer_results.items():
        for match_result in v:
            if match_result['is_final']:
                if match_result['home_score'] > match_result['away_score']:
                    match_result['winner'] = 'home'
                elif match_result['away_score'] > match_result['home_score']:
                    match_result['winner'] = 'away'
                elif match_result['home_score'] == match_result['away_score']:
                    if match_result['et'] and not match_result['pen']:
                        if match_result['home_score'] > match_result['away_score']:
                            match_result['winner'] = 'home'
                        elif match_result['away_score'] > match_result['home_score']:
                            match_result['winner'] = 'away'
                    elif match_result['pen']:
                        if match_result['penalties']['home_penalties'] > match_result['penalties']['away_penalties']:
                            match_result['winner'] = 'home'
                        elif match_result['penalties']['away_penalties'] > match_result['penalties']['home_penalties']:
                            match_result['winner'] = 'away'
            else:
                if match_result.get('aggregate_home', 0) > match_result.get('aggregate_away', 0):
                    match_result['winner'] = 'home'
                elif match_result.get('aggregate_away', 0) > match_result.get('aggregate_home', 0):
                    match_result['winner'] = 'away'
                elif match_result.get('aggregate_home', 0) == match_result.get('aggregate_away', 0):
                    if any(leg.get('et', False) for leg in match_result.get('legs', [])) and not any(leg.get('pen', False) for leg in match_result.get('legs', [])):
                        if match_result.get('aggregate_home', 0) > match_result.get('aggregate_away', 0):
                            match_result['winner'] = 'home'
                        elif match_result.get('aggregate_away', 0) > match_result.get('aggregate_home', 0):
                            match_result['winner'] = 'away'
                    elif any(leg.get('pen', False) for leg in match_result.get('legs', [])):
                        if any(leg.get('penalties', {}).get('home_penalties', 0) > leg.get('penalties', {}).get('away_penalties', 0) for leg in match_result.get('legs', [])):
                            match_result['winner'] = 'home'
                        elif any(leg.get('penalties', {}).get('away_penalties', 0) > leg.get('penalties', {}).get('home_penalties', 0) for leg in match_result.get('legs', [])):
                            match_result['winner'] = 'away'

    for layer_name in layer_results:
        bracket_data.append({
            'stage': layer_name,
            'matches': list(layer_results[layer_name]),
        })
        
    return bracket_data

def get_matchdays_info(series):
    matchdays_info = []

    matchdays = matches_calendar.MatchesCalendar.objects.filter(Series_id=series.id).\
        select_related('CompetitionCalendar').values('CompetitionCalendar__Day').distinct()

    for md in matchdays:
        if 'matchdays' not in matchdays_info:
            day = md['CompetitionCalendar__Day']

        match_results = {}
        results = list(matches_results.MatchesResults.objects.\
                    filter(MatchesCalendar__Series_id=series.id, MatchesCalendar__CompetitionCalendar__Day=day).\
                    values('MatchesCalendar_id','Team_id','NGoals','MatchesCalendar__HomeTeam_id','MatchesCalendar__AwayTeam_id'))
            
        if len(results) == 0: # match yet to be played
            empty_results = matches_calendar.MatchesCalendar.objects.filter(Series_id=series.id, CompetitionCalendar__Day=day)\
                .values('id','HomeTeam_id','AwayTeam_id')

            for empty_result in empty_results:
                match_results[empty_result['id']] = {
                    'home': get_team_name_by_id(empty_result['HomeTeam_id']),
                    'away': get_team_name_by_id(empty_result['AwayTeam_id']),
                    'home_score': '',
                    'away_score': '',
                    'played': False
            }

        for result in results:
            mc_id = result['MatchesCalendar_id']
            if mc_id not in match_results:
                match_results[mc_id] = {
                    'home': None,
                    'away': None,
                    'home_score': 0,
                    'away_score': 0,
                    'played': False
                }

            match_results[mc_id].update({
                'home': get_team_name_by_id(result['MatchesCalendar__HomeTeam_id']) if result['MatchesCalendar__HomeTeam_id'] == result['Team_id'] else match_results[mc_id]['home'],
                'away': get_team_name_by_id(result['MatchesCalendar__AwayTeam_id']) if result['MatchesCalendar__AwayTeam_id'] == result['Team_id'] else match_results[mc_id]['away'],
                'home_score': result['NGoals'] if result['MatchesCalendar__HomeTeam_id'] == result['Team_id'] else match_results[mc_id]['home_score'],
                'away_score': result['NGoals'] if result['MatchesCalendar__AwayTeam_id'] == result['Team_id'] else match_results[mc_id]['away_score'],
                'played': True
            })

            
        matchdays_info.append({
                'number': day,
                'is_live': False,
                'matches': list(match_results.values())
            })
        
        matchdays_info.sort(key=lambda x: x['number'])

    return matchdays_info


def get_groups_data_for_competition(competition_id):
    groups_data = []
    series_girone = get_all_series_girone(competition_id)

    for s in series_girone:
        group_teams = team.Team.objects.filter(Series__id=s.id).values('id','Name')
        group_matchdays = get_matchdays_info(s)
        ranking_line = ranking.Ranking.objects.filter(Q(Series_id=s.id)).values_list('RankingLine', flat=True).order_by('-Day').first()
        group_ranking = parse_ranking_line(ranking_line) if ranking_line else []

        groups_data.append({
            'id': s.id,
            'name': s.Name,
            'teams': list(group_teams),
            'matchdays': group_matchdays,
            'ranking': list(group_ranking)
        })

    return groups_data

def check_lineup_exists(teamid, day, comp_id=1):
    my_series = get_my_series(teamid, comp_id)
    lineup_exists = lineup.Lineup.objects.filter(Team=teamid, Day=day, Series__in=my_series).exists()
    return lineup_exists

def get_real_team_by_name(name):
    return real_team.RealTeam.objects.filter(Name=name).first()

def is_series_girone(series_id):
    s = series.Series.objects.get(pk=series_id)
    return s.IsGirone if s is not None else False

def get_competition_series_stages_days_mapping():
    mapping = {}
    all_cc = competition_calendar.CompetitionCalendar.objects.filter(
        Q(Season__Active=True)
    ).select_related('competition')\
        .values('Competition_id','Day','Stage','Competition_id__Name').order_by('Day')

    for cc in all_cc:
        comp_name = cc['Competition_id__Name']
        comp_id = cc['Competition_id']
        _series = get_all_series_girone(comp_id) if cc['Stage']=='Girone' else []
        _finalSeries = get_all_final_series(comp_id)
        day = cc['Day']
        stage = cc['Stage']
        if comp_id not in mapping:
            mapping[comp_id] = {"id": comp_id, "name": comp_name, "stages": {}}
        if stage != "Girone":
            _stage = _finalSeries.filter(Name=stage).first()
            if _stage is None:
                continue
            if _stage.id not in mapping[comp_id]["stages"]:
                mapping[comp_id]["stages"][_stage.id] = {"name": stage, "days": []}
            mapping[comp_id]["stages"][_stage.id]["days"].append(day)
        else: #girone
            for _s in _series:
                stage_name = _s.Name
                if _s.id not in mapping[comp_id]["stages"]:
                    mapping[comp_id]["stages"][_s.id] = {"name": stage_name, "days": []}
                mapping[comp_id]["stages"][_s.id]["days"].append(day)

    return mapping

def get_official_current_day(day_time_boundaries, teamid):
    _market = get_my_market(teamid)
    official = bet.Bet.objects.filter(
        Q(Team=teamid) &
        Q(IsOfficial=True) &
        Q(Expiration_Date__gte=day_time_boundaries[0]) &
        Q(Expiration_Date__lte=day_time_boundaries[1]) &
        Q(Market=_market.id)
    ).values('Player_id')
    
    return [o['Player_id'] for o in official]

def is_live_day():
    now = datetime.datetime.now(ZoneInfo('Europe/Rome'))
    current_day_boundaries = get_current_day_boundaries(get_current_day())
    if current_day_boundaries[0] is None or current_day_boundaries[1] is None:
        return False
    return current_day_boundaries[0] <= now <= current_day_boundaries[1]

def get_svincoli_current_day(day_time_boundaries, teamid):
    _market = get_my_market(teamid)
    svincoli = bet_history.Bet_History.objects.filter(
        Q(Svincolo=True) &
        Q(Team=teamid) &
        Q(Time__gte=day_time_boundaries[0]) &
        Q(Time__lte=day_time_boundaries[1]) &
        Q(Market=_market.id)
    ).values('Player_id')
    
    return [s['Player_id'] for s in svincoli]

def get_current_day_boundaries(current_day):
    today_matches = real_calendar.Real_calendar.objects.filter(Q(Day=current_day)&
                                                               Q(Season__Active=True)).values('Date').order_by('Date')
    if len(today_matches) == 0:
        return (None, None)
    day_time_start = today_matches.first()['Date'].astimezone(ZoneInfo(key='Europe/Rome')) if len(today_matches) > 0 else None
    day_time_end = today_matches.last()['Date'].astimezone(ZoneInfo(key='Europe/Rome')) if len(today_matches) > 0 else None
    return (day_time_start, day_time_end)

def check_day_suspended(day):
    suspended = competition_calendar.CompetitionCalendar.objects.filter(Q(Day=day)&Q(Suspended=True)).values('Day')
    return len(suspended) > 0

def get_competition_calendar_entry(competition_id, day):
    cc = competition_calendar.CompetitionCalendar.objects.filter(
        Q(Competition=competition_id) & 
        Q(Day=day) &
        Q(Season__Active=True)
    )
    return cc.first() if len(cc) > 0 else None

def is_round_trip_match(cc):
    return (cc.HomeAway & cc.Overtime) if cc is not None else False

def is_single_match_knockout(cc):
    return (cc.HomeAway == False) & (cc.Overtime == True) if cc is not None else False

def check_competition_overtime(competition_id, day):
    cc = competition_calendar.CompetitionCalendar.objects.filter(
        Q(Competition=competition_id) & Q(Day=day) & Q(Season__Active=True)).values('Overtime')
    return cc.first()['Overtime'] if len(cc) > 0 else False

def check_late_lineup(teamid, day, competition_id):
    _series = get_my_series(teamid, competition_id)

    if len(_series) == 0:
        return False

    if len(_series) > 0:
        lin = lineup.Lineup.objects.filter(
            Q(Day=day) & 
            Q(Team=teamid) & 
            Q(Series=_series[0])).values('Version').order_by('Version')

    return not (lin.first()['Version'] > (-1)) if len(lin) > 0 else False
 

def get_day_comps_lineups(day):
    teams = team.Team.objects.filter(Active=True).values('id','Name')
    team_lups_comps = {}

    for t in teams:
        t_nlineups = get_my_lineups_by_day_distinct(t['id'], day)
        t_comps = get_my_lineup_competitions_from_calendar(t['id'], day)
        
        team_lups_comps[t['id']] = {'tname':t['Name'], \
                                    'nlineups': t_nlineups['nlin'], \
                                    'ncomps': len(t_comps), \
                                    'full': t_nlineups['nlin'] - len(t_comps) == 0, \
                                    'partial': ((len(t_comps) - t_nlineups['nlin']) > 0 ) and (t_nlineups['nlin'] > 0), \
                                    'empty': len(t_comps) == 0 }

    return team_lups_comps

def get_my_lineups_competitions_by_day(teamid, day):
    return lineup.Lineup.objects.filter(
        Q(Team=teamid) & Q(Day=day) & Q(Series__Season__Active=True)).values('Series_id__Competition_id')

def get_my_lineups_by_day_distinct(teamid, day):
    return lineup.Lineup.objects.filter(
        Q(Team=teamid) & Q(Day=day) & Q(Series__Season__Active=True)
    ).aggregate(nlin=Count('Series_id', distinct=True))

def get_my_active_competitions_filtered(teamid, day):
    return competition.Competition.objects.filter(Q(Active=True) & \
        Q(Lineup=True) & \
        Q(team_competition__Team_id=teamid) & \
        Q(competitioncalendar__Day=day) & \
        Q(competitioncalendar__Season__Active=True)
    )

def get_results_calendar(series_id, day):
    results = []
    mcs = matches_calendar.MatchesCalendar.objects.filter(Q(Series_id=series_id) ) 
    
    for mc in mcs:
        ngoals_home = matches_results.MatchesResults.objects.filter(Q(MatchesCalendar_id=mc.id) & Q(Team_id=mc.HomeTeam.id)).values('NGoals')
        ngoals_away = matches_results.MatchesResults.objects.filter(Q(MatchesCalendar_id=mc.id) & Q(Team_id=mc.AwayTeam.id)).values('NGoals')

        results.append([
            f'GIORNATA {mc.CompetitionCalendar.Day}',
            mc.HomeTeam.Name,
            ngoals_home[0]['NGoals'] if len(ngoals_home) > 0 else '-',
            ngoals_away[0]['NGoals'] if len(ngoals_away) > 0 else '-',
            mc.AwayTeam.Name,
            ])
    
    return results

def is_current_day_completed():
    url = "https://publicapi.fantamaster.it/livescores/?tcache=1756165942189"
    resp = req.get(url)
    resp_content = resp.content
    resp_json = json.loads(resp_content)
    resp_day = resp_json['day']

    for score in resp_json['scores']:
        if score['time'] != C.Events.END_MATCH:
            return False, resp_day

    return True, resp_day

def clean_name(name):
    return name.replace(' ','_').replace('\'','')

def get_last_available_ranking_by_day(c_id, s_id, day):
    r = ranking.Ranking.objects.filter(Q(Competition=c_id) & Q(Series=s_id) & Q(Day__lt=day)).order_by('-Day')
    if len(r) <= 0:
        return None

    return r

def get_last_available_ranking(c_id, s_id):
    r = ranking.Ranking.objects.filter(Q(Competition=c_id) & Q(Series=s_id)).order_by('-Day')
    if len(r) <= 0:
        return None

    return r

def get_ranking(c_id, s_id, day):
    #check the first not suspended day before (any competition, since b11 is not listed as regular competition)
    if check_day_suspended(day):
        days = competition_calendar.CompetitionCalendar.objects.filter(
            Q(Suspended=False)&
            Q(Day__lt=day)&
            Q(Season__Active=True)
        ).values('Day').order_by('-Day')
        if len(days) <= 0:
            return None
        day = days[0]['Day']

    r = ranking.Ranking.objects.filter(Q(Competition=c_id) & Q(Series=s_id) & Q(Day=int(day)))
    if len(r) <= 0:
        return None

    return r

def get_days(c_id):
    return competition_calendar.CompetitionCalendar.objects.filter(
        Q(Competition=c_id)&
        Q(Suspended=False) & 
        Q(Season__Active=True)
    ).values('Day')

def get_competition_by_id(id):
    return competition.Competition.objects.get(pk=id)

def get_competition(name):
    return competition.Competition.objects.filter(Name=name)

def get_all_competitions():
    return competition.Competition.objects.all()

def get_all_active_competitions():
    return competition.Competition.objects.filter(Q(Active=True))

def get_all_live_competitions():
    return competition.Competition.objects.filter(Q(Live=True))

def get_all_live_active_competitions():
    return competition.Competition.objects.filter(Q(Active=True) & Q(Live=True))

def get_all_lineup_active_competitions():
    return competition.Competition.objects.filter(Q(Active=True) & Q(Lineup=True))

def get_my_competitions_from_calendar(teamid, day):
    return competition.Competition.objects.filter(
        id__in=matches_calendar.MatchesCalendar.objects.filter(
            (Q(HomeTeam=teamid) | Q(AwayTeam=teamid)) &
            Q(CompetitionCalendar__Day=day)
        ).values_list('CompetitionCalendar__Competition', flat=True).distinct()
    )

def get_my_lineup_competitions_from_calendar(teamid, day):
    return competition.Competition.objects.filter(Q(Lineup=True) & \
        Q(id__in=matches_calendar.MatchesCalendar.objects.filter(
            (Q(HomeTeam=teamid) | Q(AwayTeam=teamid)) &
            Q(CompetitionCalendar__Day=day) & Q(CompetitionCalendar__Season__Active=True)
        ).values_list('CompetitionCalendar__Competition', flat=True).distinct()
        )
    )

def get_my_lineup_active_competitions(my_series, day):
    return competition.Competition.objects.filter(Q(Active=True) & \
                                                  Q(Lineup=True) & \
                                                  Q(series__id__in=my_series) & \
                                                  Q(competitioncalendar__Day=day))
    #TODO modify:
    #competition.Competition.objects.filter(Q(Active=True) & \
    #                                              Q(Lineup=True) & \
    #                                              Q(team_competition__Team_id=t['id']) & \
    #                                              Q(competitioncalendar__Day=day))

def get_all_today_competitions(day):
    return competition.Competition.objects.filter(Q(Active=True) & \
                                                  Q(Live=True) & \
                                                  Q(competitioncalendar__Day=day) & \
                                                  Q(competitioncalendar__Season__Active=True))

def get_my_competitions(my_series):
    return competition.Competition.objects.filter(series__id__in=my_series)

def get_overtime_penalties(competitionid, day):
    cc= competition_calendar.CompetitionCalendar.objects.filter(
        Q(Competition=competitionid)&Q(Day=day) & Q(Season__Active=True)).values('Overtime','Penalties')
    return cc.first()['Overtime'] if len(cc)>0 else False #here we assume that if overtime is true, penalties are true too

def get_penalties(competitionid, day):
    cc= competition_calendar.CompetitionCalendar.objects.filter(Q(Competition=competitionid)&Q(Day=day) & Q(Season__Active=True)).values('Penalties')
    return cc.first()['Penalties'] if len(cc)>0 else False

def get_homeaway(competitionid, day):
    cc= competition_calendar.CompetitionCalendar.objects.filter(Q(Competition=competitionid)&Q(Day=day) & Q(Season__Active=True)).values('HomeAway')
    return cc.first()['HomeAway'] if len(cc)>0 else False

def get_all_series_from_calendar(competitionid, day):
    return series.Series.objects.filter(
        id__in=matches_calendar.MatchesCalendar.objects.filter(
            Q(CompetitionCalendar__Competition=competitionid) &
            Q(CompetitionCalendar__Day=day) &
            Q(CompetitionCalendar__Season__Active=True)
        ).values_list('Series', flat=True).distinct()
    )

def get_unica_series(competitionid):
    return series.Series.objects.filter(
        Q(Name='Unica') & 
        Q(Competition_id=competitionid))

def get_my_series_from_calendar(teamid, competitionid, day):
    return series.Series.objects.filter(
        Q(team=teamid) &
        Q(Competition=competitionid) &
        Q(id__in=matches_calendar.MatchesCalendar.objects.filter(
            (Q(HomeTeam=teamid) | Q(AwayTeam=teamid)) &
            Q(CompetitionCalendar__Day=day ) &
            Q(CompetitionCalendar__Season__Active=True)
        ).values_list('Series', flat=True).distinct())
    )

def get_my_series(teamid, competitionid=1):
    return series.Series.objects.filter(Q(team=teamid) & Q(Competition=competitionid) & Q(Season__Active=True))

def get_my_active_series(teamid, competitionid=1):
    return series.Series.objects.filter(Q(team=teamid) & Q(Competition=competitionid) & Q(Active=True) & Q(Season__Active=True))

def get_all_my_series(teamid):
    return series.Series.objects.filter(Q(team=teamid) & Q(Season__Active=True))

def get_all_active_series_by_day(competitionid, day):
    return series.Series.objects.filter(Q(Competition_id=competitionid) & Q(Active=True) & Q(Season__Active=True) & Q(competitioncalendar__Day=day))

def get_all_series(competitionid):
    return series.Series.objects.filter(Q(Competition_id=competitionid) & Q(Season__Active=True))

def get_all_final_series(competitionid):
    return series.Series.objects.filter(Q(Competition_id=competitionid) & Q(IsGirone=False) & Q(Season__Active=True))

def get_all_series_girone(competitionid):
    return series.Series.objects.filter(Q(Competition_id=competitionid) & Q(IsGirone=True) & Q(Season__Active=True))

def get_my_markets(seriesid):
    return market.Market.objects.filter(Series_id=seriesid)

def get_squads(teamid):
    return squads.Squads.objects.filter(Q(Team_id=teamid) & Q(Quarantine=False) & Q(Season__Active=True))

def get_players_by_squad(_squads):
    pl_ids = [pl.Player_id for pl in _squads]
    return player.Player.objects.filter(id__in=pl_ids).values('id','Surname','Role','RealTeam')

def get_players_by_lups(l_ups):
    _lups = []
    for l_up in l_ups:
        j = json.loads(cleanJSON(l_up.Line))
        _lups.append([v for k,v in j.items() if k not in ['mod','captain','ot','penalties']])

    pl_ids = list(set().union(*_lups))

    return player.Player.objects.filter(id__in=pl_ids).values('id','Surname','Role')

def is_any_market_active(current_day_boundaries=None):
    if current_day_boundaries == (None,None):
        return False
    
    _time = datetime.datetime.now(ZoneInfo('Europe/Rome')) if current_day_boundaries is None else \
        current_day_boundaries[0] #start of the day

    session_ = session.Session.objects.filter(Q(Begin__lte=_time) &
                                           Q(End__gte=_time))
    
    return len(session_) > 0

def get_current_session(marketid):
    nowtime = datetime.datetime.now(ZoneInfo('Europe/Rome'))

    session_ = session.Session.objects.filter(Q(Market_id=marketid) &
                                          Q(Begin__lte=nowtime) &
                                          Q(End__gte=nowtime))
    
    if(len(session_) <=0): 
        return None
    
    return session_[0]

def get_my_market(teamid=None, userid=None):
    if teamid is None and userid is None:
        return
    if(userid is not None):
        teamid = get_user_team(userid)['id']

    myseries = get_my_series(teamid)
    if(len(myseries) <= 0): 
        return
    mymarkets = get_my_markets(myseries[0].id)
    if(len(mymarkets) <= 0): 
        return
    return mymarkets[0]

def get_my_svincolati(team, session=None):
    svincoli_list = \
        bet_history.Bet_History.objects.filter(Q(Team=team) & Q(Svincolo=True) & Q(Session_svincolo=session)) if session is not None else \
        bet_history.Bet_History.objects.filter(Q(Team=team) & Q(Svincolo=True))
    
    return [s.Player_id for s in svincoli_list]

def get_all_players_my_series(teamid, filtered_teams_ids, my_svincoli_current_session, my_market):

    bet_qs = bet.Bet.objects.filter(
        Player_id=OuterRef('pk'),
        Team_id__in=filtered_teams_ids,
        Market_id=my_market
    ).order_by('id')

    expired_bet_exists = bet.Bet.objects.filter(
        Player_id=OuterRef('pk'),
        Team_id__in=filtered_teams_ids,
        Market_id=my_market,
        IsExpired=True
    )

    has_my_team_bet = bet.Bet.objects.filter(
        Player_id=OuterRef('pk'),
        Team_id=teamid,
        Market_id=my_market
    )

    return player.Player.objects.filter(
        RealTeam__isnull=False,
        Status='A',
    ).exclude(
        id__in=my_svincoli_current_session
    ).annotate(
        bet__Amount=Subquery(bet_qs.values('Amount')[:1]),
        bet__Team_id__Name=Subquery(bet_qs.values('Team_id__Name')[:1]),
        bet__IsExpired=Subquery(bet_qs.values('IsExpired')[:1]),
        bet__Carognata=Subquery(bet_qs.values('Carognata')[:1]),
        bet__Expiration_Date=Subquery(bet_qs.values('Expiration_Date')[:1]),

        has_my_team_bet=Exists(has_my_team_bet),
        has_expired_bet=Exists(expired_bet_exists)
    ).filter(
        has_expired_bet=False,
        has_my_team_bet=False
    ).order_by('id').values(
        'id', 'Surname', 'Name', 'Role', 'RealTeam__Name', 'Quotation',
        'bet__Amount', 'bet__Team_id__Name', 'bet__IsExpired',
        'bet__Carognata', 'bet__Expiration_Date',
        'squads__Years', 'Status'
    ).distinct('id')

def get_players_my_series(filter_role, teamid, filtered_teams_ids, my_svincoli_current_session, my_market):
              #~
    bet_qs =  bet.Bet.objects.filter(
        Player_id=OuterRef('pk'),
        Team_id__in=filtered_teams_ids,
        Market_id=my_market
    ).order_by('id')
    
    return player.Player.objects.filter(
        Role=filter_role,
        RealTeam__isnull=False,
        Status='A',
    ).exclude(
        Q(bet__Team_id=teamid) & Q(bet__Market_id=my_market)
    ).exclude(
        Q(id__in=my_svincoli_current_session)
    ).annotate(
      bet__Amount=Coalesce(Subquery(bet_qs.values('Amount')[:1]), Value(None)),
      bet__Team_id__Name=Coalesce(Subquery(bet_qs.values('Team_id__Name')[:1]), Value(None)),
      bet__IsExpired=Coalesce(Subquery(bet_qs.values('IsExpired')[:1]), Value(None)),
      bet__Carognata=Coalesce(Subquery(bet_qs.values('Carognata')[:1]), Value(None)),
      bet__Expiration_Date=Coalesce(Subquery(bet_qs.values('Expiration_Date')[:1]), Value(None)),
    ).exclude(
        Q(bet__IsExpired=True) &
        Q(bet__Team_id__in=filtered_teams_ids)
    ).values(
        'id', 'Surname', 'Name', 'Role', 'RealTeam__Name',
        'bet__Amount', 'bet__Team_id__Name', 'bet__IsExpired','bet__Carognata','bet__Expiration_Date'
    ).distinct('id')

        
def check_max_n_bets(teamid, role):
    qplayer = squads.Squads.objects.\
      filter(Q(Team_id=teamid) & Q(Quarantine=True)).first()
    
    if(qplayer):
        idq = qplayer.Player_id   
    else:
        idq = -1

    num_bets = bet.Bet.objects.\
        filter(Q(Team_id=teamid) & Q(Market_id=get_my_market(teamid).id) & Q(Player__Role=role)).\
        exclude(Q(Player_id = idq)).\
        aggregate(Count('id'))
        
    max_num = \
            C.NUM_GK if role == "P" else \
            C.NUM_DEF if role == "D" else \
            C.NUM_CC if role == "C" else \
            C.NUM_FW if role == "A" else -1
    
    return (
        True if num_bets['id__count'] < max_num else False
    )


def get_current_bets_amount(teamid, marketid):
    sum = bet.Bet.objects.filter(Q(Team_id=teamid) & \
                                 Q(Market_id=marketid)).aggregate(Sum('Amount'))['Amount__sum']
    return sum if sum is not None else 0

def update_balance_latelineup(bal):
    n_non_schierate = bal.N_formazioni_non_schierate
    bal.N_formazioni_non_schierate = n_non_schierate + 1
    bal.save()

def get_balance_for_bets(teamid, balance_max, marketid=None):
    if marketid is None:
        my_market = get_my_market(teamid)
        marketid = my_market.id

    sum = bet.Bet.objects.filter(Q(Team_id=teamid) & Q(Market_id=marketid)).aggregate(Sum('Amount'))
    #missing slot count
    num_active_bets = bet.Bet.objects.filter(Q(Team_id=teamid) & Q(Market_id=marketid)).aggregate(Count('id'))
    num_missing_slots = (C.NUM_SLOTS - num_active_bets['id__count']) - 1

    return ((balance_max - sum['Amount__sum'] - num_missing_slots) if sum['Amount__sum'] is not None else balance_max - num_missing_slots)

def get_my_best_bets(teamid, marketid):
	
    qplayer = squads.Squads.objects.\
      filter(Q(Team_id=teamid) & Q(Quarantine=True)).first()
    
    bets = bet.Bet.objects.\
        filter(Q(Team_id=teamid) & Q(Market_id=marketid)).\
        values('Amount','Expiration_Date', 'Session_id',
               'IsExpired','id','Team_id','IsOfficial','Carognata', 
               'Player_id__Role', 'Player_id__RealTeam__Name', 
               'Player_id__Quotation', 'Player_id__Status', 'Player_id','Player_id__Surname',
               'squads__Years').distinct('Player_id')
               
    if(qplayer is not None):
       bets = bets.exclude(Q(Player_id=qplayer.Player_id))

    return bets   
       
       
def list_my_best_bets(mbb):
    ls = list(mbb).__str__()
    lsr = ls.replace('\'','"')
    lsr = lsr.replace('True', 'true')
    lsr = lsr.replace('False','false')
    return lsr

def get_balance_obj(teamid):
    return balance.Balance.objects.\
        filter(Team_id=teamid)

def get_balance(teamid):
    return balance.Balance.objects.\
        filter(Q(Team_id=teamid) & Q(Season__Active=True)).\
        values('Purchases_amount','Purchases_max','Wages_amount','Wages_max','N_carognate','N_svincoli')

def get_all_team_players():
    return player.Player.objects.filter(bet__Market__Series__Season__Active=True).\
        values('id','Surname','Name','Role','bet__Team_id','bet__Amount',\
               'bet__IsExpired','bet__Carognata','bet__Expiration_Date')

                
def send_bet(data):
    bet_obj =  bet.Bet_Obj()
    bet_obj.Amount = int(data['betamount'])
    bet_obj.Player = data['playerid']
    bet_obj.Expiration_Date = data['exp_date']
    bet_obj.Team = data['userteamid']
    bet_obj.Slot = data['slot']
    bet_obj.Market = data['market']
    bet_obj.Session = data['session']
    
    carognata = data['carognata']
    balance_max = data['balancemax']
    exp_date_obj = datetime.datetime.strptime(bet_obj.Expiration_Date, '%d/%m/%Y, %H:%M:%S').\
        replace(tzinfo=datetime.timezone.utc)   

    player_ = get_object_or_404(player.Player, id=bet_obj.Player)
    user_team = get_object_or_404(team.Team, id=bet_obj.Team) #TODO: how to avoid this double fetch?
    market_ = get_object_or_404(market.Market, id=int(bet_obj.Market))
    session_ = session.Session.objects.get(pk=bet_obj.Session)

    my_bal = get_balance_obj(bet_obj.Team)[0]
    ncarognate = my_bal.N_carognate
    balance_for_bets = get_balance_for_bets(bet_obj.Team, int(balance_max))

    if(not check_max_n_bets(user_team.id, player_.Role)):
        return C.SendBetReturnValues(C.SendBetResult.BET_SLOT_EXCEED)

    if(bet_obj.Amount > balance_for_bets):
        return C.SendBetReturnValues(C.SendBetResult.BET_OVERFLOW)

    try:
        bet_old = bet.Bet.objects.filter(Q(Player=player_) & Q(Market=market_))
        if len(list(bet_old)) == 1: #there is an old best bet
            _bet_old = bet_old[0]

            if(_bet_old.IsExpired == True):
                return C.SendBetReturnValues(
                    C.SendBetResult.BET_EXPIRED)

            if(bet_obj.Amount <= _bet_old.Amount):
                return C.SendBetReturnValues(
                    C.SendBetResult.BET_UNDERFLOW)

            bet_history_new = bet_history.Bet_History(
                Amount=_bet_old.Amount,
                Player=_bet_old.Player,
                Team=_bet_old.Team,
                Market=market_,
                Session=session_,
                Carognata = True if carognata==True else False,
                Expiration_Date=_bet_old.Expiration_Date
            )
            bet_history_new.save()

            bet_old.delete() #remove old bet

        bet_new = bet.Bet(Amount=bet_obj.Amount,
                        Player = player_,
                        Team = user_team,
                        Expiration_Date=exp_date_obj,
                        Slot='unused',
                        Market=market_,
                        Session=session_)

        bet_new.save()

        if(carognata == True):
            
            my_bal.N_carognate = ncarognate + 1

            if(my_bal.N_carognate > session_.Ncarognate): #penalty
                my_bal.Wages_max = my_bal.Wages_max - 1

            my_bal.save()
    
    except Exception as e:
        # if(bet_new is not None):
        #     bet_new.delete() #rollback
        #RESCUE OLD BET FROM BET_HISTORY TODO
        raise Exception(e) 

    new_balance_for_bets = get_balance_for_bets(bet_obj.Team, int(my_bal.Purchases_max), marketid=market_.id)
    new_bets_amount = get_current_bets_amount(bet_obj.Team, marketid=market_.id)

    return C.SendBetReturnValues(
            bet_result=C.SendBetResult.BET_OK, 
            bet_id=bet_new.id,
            residual=(my_bal.Purchases_max  - new_bets_amount),  
            new_balance_for_bets=new_balance_for_bets, 
            n_carognate=ncarognate + 1 if (carognata == True) else ncarognate, 
            total=my_bal.Purchases_max)

def finalize_bet(data):

    fin_obj = squads.Squads_Obj()
    fin_obj.Amount = data['amount']
    fin_obj.Player = data['playerid']
    fin_obj.Team = data['userteamid']

    player_ = get_object_or_404(player.Player, id=fin_obj.Player)
    user_team = get_object_or_404(team.Team, id=fin_obj.Team)
    my_market_id = get_my_market(fin_obj.Team).id
    my_market = get_object_or_404(market.Market, id=my_market_id)
    last_bet = bet.Bet.objects.filter(Q(Player=player_) & Q(Market=my_market))

    if(len(last_bet) <= 0): #very rare case, only during tests
        return
    
    if(last_bet[0].IsOfficial == True):
        return C.ErrorCodes.ALREADY_OFFICIAL
    
    last_bet.update(IsOfficial=True)

    fin_new = squads.Squads(
        Amount=fin_obj.Amount,
        Player = player_,
        Team = user_team,
        Last_bet = last_bet[0],
        Season = get_current_season()
    )
    fin_new.save()            

    
def get_user_team(userid):
    return team.Team.objects.filter(Users__id=userid).values('id','Name','LogoPath')[0]

def get_my_players_filtered(filter_role, teamid):
    return squads.Squads.objects.\
        filter(Team_id=teamid).\
        filter(Player__Role=filter_role).\
        filter(Quarantine=False).\
        filter(Season__Active=True).\
        values(
            'id',
            'Player__id',
            'Player__Surname',
            'Player__RealTeam__Name',
            'Amount',
            'Player__Role',
            'Player__RealTeam__id',
            'Years',   # <--- ADD THIS
            'Salary'   # <--- ADD THIS
        ).\
        order_by('Player__Surname')
        
        
def complete_list(l, num_max, role):
    if(len(l) < num_max):
        for _ in range(num_max - len(l)):
            l.append({"id": "-1", "Role":role})
    
    return l

def get_current_day(competition_id=""):
    day = config.Config.objects.filter(Name="CurrentDay").first()
    return day.Value

def get_team_by_userid(userid):
    t = team.Team.objects.filter(Users__id=userid).values('id','Name')
    if len(t) > 0:
        return t[0]
    return None

def get_team_name_by_id(teamid):
    return team.Team.objects.filter(id=teamid).values('Name')[0]['Name']

def get_team_by_name(tname):
    return team.Team.objects.get(Name=tname)

def get_all_lineups(teamid, day, seriesid):
    return lineup.Lineup.objects.filter(Team=teamid, Day=day, Series=seriesid).order_by('Version')

def get_last_valid_lineup(teamid, comp_id=1):
    my_series = get_my_series(teamid, comp_id)
    all_lups = lineup.Lineup.objects.filter(Team=teamid, Series__in=my_series).order_by('-Version').order_by('-Day')
    if len(all_lups) <= 0:
        return None
    
    return list(all_lups)[0]

def get_last_lineup(teamid, day, comp_id=1):
    my_series = get_my_series(teamid, comp_id)
    return lineup.Lineup.objects.filter(Team=teamid, Day=day, Series__in=my_series).order_by('-Version')[:1]

def save_last_valid_lineup(_lineup, day, seriesid):
    last_lineup_late = lineup.Lineup(
        Line = _lineup.Line,
        Day = day,
        Version = -1, #LATE LINEUP
        Team = _lineup.Team,
        Timestamp = datetime.datetime.now(),
        Series = series.Series.objects.get(pk=seriesid),
        HideLineup = _lineup.HideLineup,
        ModNoGk = _lineup.ModNoGk,
        LateEdit = False
    )

    last_lineup_late.save()

def save_lineup(lineup_info):
    lineup_new = lineup.Lineup(
        Line = lineup_info['line'],
        Day = lineup_info['day'],
        Version = lineup_info['version'],
        Team = get_object_or_404(team.Team, id=lineup_info['team']),
        Timestamp = lineup_info['timestamp'],
        Series = lineup_info['series'],
        HideLineup = lineup_info['hideLineup'],
        ModNoGk = lineup_info['modNoGk'],
        LateEdit = lineup_info['late_edit']
        )

    lineup_new.save()

def cleanJSON(jsonData):
    jsonData = jsonData.replace("'","\"") #retransform after HTML form
    jsonData = jsonData.replace("\"{","{").replace("}\"","}") #remove extra " with {
    jsonData = jsonData.replace("\\","") #remove extra \

    return jsonData    

def check_day_already_started(day):
    today_matches = real_calendar.Real_calendar.objects.filter(Q(Day=day) & Q(Season__Active=True)).values('Date').order_by('Date')
    day_time_limit = today_matches.first()['Date'].astimezone(ZoneInfo(key='Europe/Rome')) if len(today_matches) > 0 else None
    if day_time_limit is None:
        return False, datetime.datetime.now(ZoneInfo('Europe/Rome'))
    return datetime.datetime.now(ZoneInfo('Europe/Rome')) >= day_time_limit, day_time_limit

def free_player(data):
    player_id = data.get("playerid")
    team_id = data.get("teamid")
    market = data.get("market")
    session_svincolo = get_current_session(market).id if get_current_session(market) is not None else None
    if player_id is None or team_id is None or market is None or session_svincolo is None:
        return C.ErrorCodes.INVALID_PARAMETERS

    _bet = bet.Bet.objects.filter(Q(Player=player_id) & 
                                  Q(Team=team_id) &
                                  Q(Market=market) &
                                  Q(IsOfficial=True)).first()

    if(_bet is None):
        return C.ErrorCodes.BET_NOT_FOUND

    _squad = squads.Squads.objects.filter(
        Q(Team=_bet.Team_id) & 
        Q(Player=_bet.Player) &
        Q(Season__Active=True)
    ).first()

    if(_squad is None):
        return C.ErrorCodes.PLAYER_NOT_IN_SQUAD
    _squad.delete()

    bet_history_new = bet_history.Bet_History(
            Amount=_bet.Amount,
            Player=_bet.Player,
            Team=_bet.Team,
            Market=_bet.Market,
            Session=_bet.Session,
            Carognata = True if _bet.Carognata==True else False,
            Svincolo = True,
            Session_svincolo = session.Session.objects.get(pk=session_svincolo)
            )
    
    bet_history_new.save()

    #if player estero/B, do not count svincolo
    if _bet.Player.Status != 'A':
        _bet.delete()
        return

    my_bal = get_balance_obj(_bet.Team_id)
    if len(my_bal) <= 0:
        return
    
    my_bal = my_bal[0]
    my_bal.N_svincoli = my_bal.N_svincoli + 1

    max_svincoli = _bet.Session.Nsvincoli

    if(my_bal.N_svincoli > max_svincoli): #penalty
        my_bal.Purchases_max = my_bal.Purchases_max - 1

    my_bal.save()

    _bet.delete()

def calculate_n_goals(fp_total): #replicate of live utilities method to avoid circular ref
    diff = fp_total - C.Various.BASE_SCORE
    if (diff < 0):
        return 0
    
    return int(diff / C.Various.THRESHOLD_GOL) + 1    

def get_scores(t_id):
    results_fp = matches_results.MatchesResults.objects.filter(Team=t_id).order_by('id').values('Fp')
    fps = []
    for res in list(results_fp):
        fps.append(res['Fp'])
    
    return fps

def count_non_schierate(t_id):
    non_schierate = matches_results.MatchesResults.objects.filter(Q(Penalizations__gt=0)&Q(Team=t_id)).aggregate(num=Count("MatchesCalendar__CompetitionCalendar__Day"))
    return non_schierate['num']

def check_penalties(t_id, day, comp_id):
    l = get_last_lineup(t_id, day, comp_id=comp_id)[0]

    if l.Version > 0:
        return 3, 1, 0 #standard
    
    if l.Version < 0: #TODO: in case of recalculation this counter is wrong! use march_result instead
        n_non_schierate = count_non_schierate(t_id)
        if n_non_schierate <= C.MAX_NON_SCHIERATE:
            return 0, 0, 0 #0 pt
        else:
            return -1, -1, -1 #-1 pt 

def check_contract(squad_contracts, role, years_signed):

    n_contracts_per_role = sum(squad_contracts.get(role, {}).values()) if role in squad_contracts else 0
    max_per_role = C.Constant_Dicts.Roles.get(role, 0)
    at_least_one_annual = squad_contracts.get(role, {})['1'] >= C.MIN_ANNUAL_CONTRACTS_PER_ROLE if role in squad_contracts and '1' in squad_contracts[role] else False

    if n_contracts_per_role == (max_per_role -1):
        if years_signed == 2 or years_signed == 3 and not at_least_one_annual: #we need at least one annual contract
            return C.ErrorCodes.MIN_ANNUAL_CONTRACTS_PER_ROLE_NEEDED

    if years_signed == 3:
        current_triennals_per_role = squad_contracts[role][years_signed.__str__()] if role in squad_contracts and years_signed.__str__() in squad_contracts[role] else 0
        if current_triennals_per_role >= C.MAX_TRIENNAL_CONTRACTS_PER_ROLE:
            return C.ErrorCodes.MAX_TRIENNAL_CONTRACTS_PER_ROLE_EXCEEDED

    return True

def sign_contract(contract_data):

    player_ = get_object_or_404(player.Player, id=contract_data['playerid'])
    team_ = get_object_or_404(team.Team, id=contract_data['teamid'])
    season = get_current_season()
    years_signed = contract_data['years']
    rounded_wage = round(player_.Quotation * C.WAGE_MULTIPLIER) #0.5
    total_wage = rounded_wage * years_signed

    squad_contracts = get_signed_contracts(team_.id)
    check_result = check_contract(squad_contracts, player_.Role, years_signed)
    if(check_result != True): #error code returned
        return check_result

    existing_squad = squads.Squads.objects.filter(Q(Player=player_) & Q(Team=team_) & Q(Season=season))

    if existing_squad.exists():
        existing_squad.update(Years=years_signed, Salary=total_wage)
    else:
        return C.ErrorCodes.PLAYER_NOT_IN_SQUAD

    wages_amount = squads.Squads.objects.filter(Q(Team=team_) & Q(Season__Active=True)).aggregate(
        Sum('Salary'))['Salary__sum']

    balance_ = get_balance(team_.id)
    # wages_amount = balance_[0]['Wages_amount'] if len(balance_) > 0 else 0
    # wages_amount += total_wage

    balance_.update(Wages_amount=wages_amount)

    return {'wages_amount': wages_amount, 'player_wage': total_wage}

