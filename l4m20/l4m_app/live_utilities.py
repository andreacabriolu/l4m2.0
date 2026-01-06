import datetime
from zoneinfo import ZoneInfo
from .models import *
import json
from l4m20 import constants as C
import statistics
from . import utilities as U
from django.db.models import Q
import requests as req
from itertools import islice, cycle

def add_extratime_penalties_votes(votes, extra_goals, penalties):
    #add extratime goals
    votes[1][9] += extra_goals #NGoals, BAD!

    if penalties is None or len(penalties) == 0:
        votes[1].append(1) #only extratime
        return votes

    votes[1].append(2) #extratime + penalties
    #add penalties goals
    pen_points = sum([1 for v in penalties.values() if (v)]) #count how many made at least one point

    #add to votes items
    votes[1][9] += pen_points #NGoals

    return votes

def extract_votes_for_penalties(pen_players, votes):
    votes_tit = votes[0]
    tit_players = [int(v.Player.id) for v in votes_tit]
    pen_players = [int(p) for p in pen_players]

    pen_votes = {}

    for p in pen_players:
        if p in tit_players:
            matching_vote = next((v.Vote for v in votes_tit if int(v.Player.id) == p), None)
            pen_votes[p] = matching_vote
    
    #complete the list if needed
    diff = set(tit_players) - set(pen_players)
    for d in diff:
        pen_votes[d] = next((v.Vote for v in votes_tit if int(v.Player.id) == d), None)

    return pen_votes

def calculate_penalties_votes(lineup_home, lineup_away, votes_home, votes_away):
    if lineup_home is None or lineup_away is None:
        return 0,0
    
    pen_results_home = {}
    pen_results_away = {}

    line_home = json.loads(U.cleanJSON(lineup_home.Line))
    pen_players_home = line_home['penalties'] if 'penalties' in line_home else []
    votes_tit_home = votes_home[0]

    line_away = json.loads(U.cleanJSON(lineup_away.Line))
    pen_players_away = line_away['penalties'] if 'penalties' in line_away else []
    votes_tit_away = votes_away[0]

    gk_home_vote = votes_tit_home[0].Vote #home goalkeeper pure vote
    gk_away_vote = votes_tit_away[0].Vote #away goalkeeper pure vote

    pen_home_votes = extract_votes_for_penalties(pen_players_home, votes_home)
    pen_away_votes = extract_votes_for_penalties(pen_players_away, votes_away)

    #match the gk vote with opponent's players votes. If equal, player makes a point.
    #round the list until 11 times
    
    #remove None from list
    pen_home_votes = {k: v for k, v in pen_home_votes.items() if v is not None}
    pen_away_votes = {k: v for k, v in pen_away_votes.items() if v is not None}

    pen_home_votes_list = list(pen_home_votes.items())
    phv_size = len(pen_home_votes_list)
    pen_away_votes_list = list(pen_away_votes.items())
    pav_size = len(pen_away_votes_list)

    for p_id,p_vote in pen_home_votes_list:
        pen_results_home[p_id] = True if p_vote >= gk_away_vote else False

    for p_id,p_vote in pen_away_votes_list:
        pen_results_away[p_id] = True if p_vote >= gk_home_vote else False

    #take first 5 penalties
    first_5_home = dict(islice(pen_results_home.items(), 5))
    first_5_away =  dict(islice(pen_results_away.items(), 5))
    scores_home = [1 if v else 0 for v in first_5_home.values()]
    scores_away = [1 if v else 0 for v in first_5_away.values()]
    
    if sum(scores_home) == sum(scores_away):
        #sudden death
        for i in range(5,11):
            home_item = list(pen_results_home.items())[i] #WARNING: TODO cycle
            away_item = list(pen_results_away.items())[i]
            home_score = 1 if home_item[1] else 0
            away_score = 1 if away_item[1] else 0

            scores_home.append(home_score)
            scores_away.append(away_score)
            if sum(scores_home) != sum(scores_away):
                break
    else:
        pen_results_home = first_5_home
        pen_results_away = first_5_away

    return {'pen_results_home': pen_results_home, 'pen_results_away': pen_results_away}

def calculate_n_ot_goals(ot_score):
    diff = ot_score - C.Various.OT_BASE_SCORE
    if (diff < 0):
        return 0
    
    return int(diff / C.Various.OT_THRESHOLD_GOL) + 1

def calculate_extratime_goals(votes, lineup):
    if lineup is None:
        return 0
    
    line = json.loads(U.cleanJSON(lineup.Line))
    ot_players = line['ot'] if 'ot' in line else []
    votes_ris = votes[2]

    ot_votes_map = {}
    ot_score = sum([v.TotVote for v in votes_ris if v.TotVote is not None and v.Player.id in ot_players])
    ot_goals = calculate_n_ot_goals(ot_score)

    for v in votes_ris:
        if v.Player.id in ot_players and v.TotVote is not None:
            ot_votes_map[v.Player.id] = v.TotVote

    return ot_goals, ot_votes_map

def check_match_for_extratime(home_team_id, away_team_id, votes_home, votes_away, day, comp_id, seriesid):
    is_round_trip = U.is_round_trip_match(day, comp_id)
    if is_round_trip:
        first_leg_results = (
            matches_results.MatchesResults.objects
            .select_related(
                "MatchesCalendar",
                "MatchesCalendar__CompetitionCalendar"
            )
            .filter(
                MatchesCalendar__CompetitionCalendar__Competition_id=comp_id,
                MatchesCalendar__CompetitionCalendar__Day__lt=day,
                MatchesCalendar__CompetitionCalendar__HomeAway=True,
                MatchesCalendar__Series_id=seriesid,
                MatchesCalendar__HomeTeam_id=away_team_id,
                MatchesCalendar__AwayTeam_id=home_team_id
            )
            .order_by("-MatchesCalendar__CompetitionCalendar__Day")
        )

        if first_leg_results:
            home_goals_first_leg = first_leg_results.filter(Home=True).first().NGoals
            away_goals_first_leg = first_leg_results.filter(Home=False).first().NGoals

            #current leg result
            if votes_home is None or votes_away is None:
                return False
            home_goals_current_leg = votes_home[1][9] #BAD! change to dict!
            away_goals_current_leg = votes_away[1][9] #BAD!
            
            #aggregate score
            home_agg = home_goals_first_leg + away_goals_current_leg
            away_agg = away_goals_first_leg + home_goals_current_leg

            if home_agg == away_agg:
                return True #match went to extratime
            
    else:
        #single match knockout
        if votes_home is None or votes_away is None:
            return False
        home_goals = votes_home[1][9] #BAD! change to dict!
        away_goals = votes_away[1][9] #BAD!
        if home_goals == away_goals:
            return True #match went to extratime
        
    return False

def create_live_ranking(all_scores, last_ranking):
    results_map = {}

    for score in all_scores:
        ht = U.get_team_by_name(score[0][0]).id
        at = U.get_team_by_name(score[1][0]).id
        hp = score[0][1]
        ap = score[1][1]
        last_ranking_home = [item[ht.__str__()] for item in last_ranking if ht.__str__() in item.keys()]
        last_ranking_away = [item[at.__str__()] for item in last_ranking if at.__str__() in item.keys()]
        if len(last_ranking_home) <=0 or len(last_ranking_away)<=0:
            continue
        ht_pt = last_ranking_home[0]['pt']
        at_pt = last_ranking_away[0]['pt']
        results_map[score[0][0]] = ht_pt + (C.WIN_PT if int(hp) > int(ap) else C.LOSE_PT if int(hp) < int(ap) else C.DRAW_PT)
        results_map[score[1][0]] = at_pt + (C.LOSE_PT if int(hp) > int(ap) else C.WIN_PT if int(hp) < int(ap) else C.DRAW_PT)

    return sorted(results_map.items(),key=lambda kv: kv[1], reverse=True)

def get_lineup_to_show(_team, day, comp_id, overtime):
    l = U.get_last_lineup(_team, day, comp_id=comp_id)
    if(len(l) <= 0 and overtime):
        last_valid_l = U.get_last_valid_lineup(_team.id)

    lineup_to_show = _team.Name #base

    if not overtime:
        if len(l) > 0:
            lineup_to_show = l[0]
        else:
            lineup_to_show = _team.Name

    if overtime:
        if len(l) > 0:
            lineup_to_show = l[0]
        else:
            lineup_to_show = last_valid_l
            
    else:  #filter for historical data
        lineup_to_show = l[0] if len(l)> 0 else _team.Name #always valued because we SHOULD save the lineup

    return lineup_to_show

def get_my_couples_from_calendar(teamid, day):
    return matches_calendar.MatchesCalendar.objects.filter(
        (Q(HomeTeam=teamid) | Q(AwayTeam=teamid)) &
        Q(CompetitionCalendar__Day=day)
    )

def format_votes(mr):
    _votes_tit = U.cleanJSON(mr.Votes_Tit)
    _votes_tit = _votes_tit.replace('<class "str">','')
    _votes_tit = _votes_tit.replace('<class "int">','')
    votes_tit_j = json.loads(_votes_tit)
    
    _votes_ris = U.cleanJSON(mr.Votes_Ris)
    _votes_ris = _votes_ris.replace('<class "str">','')
    _votes_ris = _votes_ris.replace('<class "int">','')
    votes_ris_j = json.loads(_votes_ris)

    votes_tit = remake_votes_obj(votes_tit_j)
    items = remake_items(mr)
    votes_ris = remake_votes_obj(votes_ris_j)
    
    return votes_tit, items, votes_ris

def get_matches_results(couples):
    return [matches_results.MatchesResults.objects.filter(MatchesCalendar=couple[2]) for couple in couples]

def get_votes_total(b11_lineup, home=True, homeAway=False):
    votes_tit = []
    votes_ris = []
    _items = []

    module = b11_lineup['module']

    _items.append(home)
    _items.append(b11_lineup['t'].Name)

    _items.append(b11_lineup['partial_score'])
    _items.append(b11_lineup['modif_tot'])
    _items.append(b11_lineup['modif'])
    _items.append(b11_lineup['bcaptain'])
    _items.append(b11_lineup['no_yellow_bonus'])
    _items.append(b11_lineup['all_six_bonus'])
    bonus_home = get_bonus_home(homeAway, home)
    _items.append(b11_lineup['score'] + bonus_home)

    n_goals = calculate_n_goals(b11_lineup['score'] + bonus_home)
    _items.append(n_goals)
    _items.append(module)    
    _items.append('same_module')
    _items.append(b11_lineup['modifier_from_no_gk'])
    _items.append(0) #missing slots
    _items.append(1) #version
    if homeAway:
        _items.append(1 if home else (-1))
    else:
        _items.append(0)

    tits = b11_lineup['players'][:11]
    riss = b11_lineup['players'][11:]
    
    votes_tit = [vt['player_stats'] for vt in tits]
    votes_ris = [vr['player_stats'] for vr in riss]

    return votes_tit, _items, votes_ris

def enrich_and_sort_players_live(teamid, current_day, live_votes, live_teams, already_played_teams, getForCalculation=False):

    mysquads = U.get_squads(teamid)
    players = U.get_players_by_squad(mysquads)

    enriched_players = []
    cap_id = -1 #not used for b11

    for squad_pl in players:
        votes = []

        pl = player.Player.objects.get(pk=squad_pl['id'])
        already_played = check_already_played(pl.RealTeam, already_played_teams, current_day) if getForCalculation == False else True

        #check if player is LIVE
        if pl.id in live_votes:
            _live_vote = live_votes[pl.id]
            votes = (adjust_vote_obj(_live_vote, cap_id) if _live_vote.Vote > 0 else \
                         adjust_vote_obj(_live_vote, cap_id, empty=True))
        #CASE player not called
        elif(pl.id not in live_votes and pl.RealTeam.Name in live_teams):
            votes = (make_not_called_vote_obj(pl.id, cap_id))
        else:
        #player NOT LIVE
            _vote = vote.Vote.objects.filter(Q(Player_id=pl.id) & Q(Day=current_day))
            votes = (make_vote_obj(_vote[0], cap_id) if isValid(_vote) else \
                         make_empty_vote_obj(pl.id, cap_id, already_played, current_day))

        pl.votes = votes
        enriched_players.append(pl)

    #sort by role

    keepers = [ep for ep in enriched_players if ep.Role=='P']
    defs = [ep for ep in enriched_players if ep.Role=='D']
    ccs = [ep for ep in enriched_players if ep.Role=='C']
    fws = [ep for ep in enriched_players if ep.Role=='A']

    sorted_players = {
        'P': sorted(
        keepers,
        key=lambda p: (
            p.votes.TotVote if p.votes.TotVote is not None else -1,
            p.votes.Vote if p.votes.Vote is not None else -1
        ),
        reverse=True
        ),
        'D': sorted(
        defs,
        key=lambda p: (
            p.votes.TotVote if p.votes.TotVote is not None else -1,
            p.votes.Vote if p.votes.Vote is not None else -1
        ),
        reverse=True
        ),
        'C': sorted(
        ccs,
        key=lambda p: (
            p.votes.TotVote if p.votes.TotVote is not None else -1,
            p.votes.Vote if p.votes.Vote is not None else -1
        ),
        reverse=True
        ),
        'A': sorted(
        fws,
        key=lambda p: (
            p.votes.TotVote if p.votes.TotVote is not None else -1,
            p.votes.Vote if p.votes.Vote is not None else -1
        ),
        reverse=True
        )
    }

    return sorted_players


def get_b11_lineup(teamid, day, live_votes, live_teams, already_played_teams, getForCalculation=False):
    players = enrich_and_sort_players_live(teamid, day, live_votes, live_teams, already_played_teams, getForCalculation)
    b11_live = pick_best_11(players['P'],players['D'],players['C'],players['A'])
    
    return b11_live

def get_best_11(team_ids_names, day, live_votes, live_teams, already_played_teams, getForCalculation=False):
    all_best = []

    # crea best 11 per ogni squadra
    for tid,name in team_ids_names:
        best = get_b11_lineup(tid, day, live_votes, live_teams, already_played_teams, getForCalculation)
        if(best):
            best["team_id"]=tid
            best["team_name"]=name
                            
        all_best.append(best)

    return all_best

def fill_with_events(events, votes): 
    
    for event in events:
        
        _type = event['type']
        if 'player' in event: 
            _player = U.clean_name(event['player'])
        match _type:
            case C.Events.YELLOW_RED_CARD:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]
                
                vote = votes[pl.id]
                vote.Yel = 0
                vote.YelRed = 1

            case C.Events.YELLOW_CARD:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]
                
                vote = votes[pl.id]
                vote.Yel = 1

            case C.Events.RED_CARD:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]
                
                vote = votes[pl.id]
                vote.Yel = 0
                vote.Red = 1

            case C.Events.GOAL:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]
                
                if event['details'] != '':
                    _player_ass = U.clean_name(event['details'])
                    pl_assist = player.Player.objects.filter(Surname=_player_ass)
                    if len(pl_assist) > 0:
                        pl_assist = pl_assist[0]
                        vote = votes[pl_assist.id]
                        vote.AssS = vote.AssS + 1

                vote = votes[pl.id]
                vote.GoalSc = vote.GoalSc + 1

            case C.Events.GOAL_TAKEN:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]

                vote = votes[pl.id]
                vote.GoalTa = vote.GoalTa + 1

            case C.Events.PENALTY_SCORED:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]

                vote = votes[pl.id]
                vote.PenSc = vote.PenSc + 1

            case C.Events.PENALTY_MISSED:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]

                vote = votes[pl.id]
                vote.PenMi = vote.PenMi + 1

            case C.Events.PENALTY_SAVED:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]

                vote = votes[pl.id]
                vote.PenSa = vote.PenSa + 1

            case C.Events.OWN_GOAL:
                pl = player.Player.objects.filter(Surname=_player)
                if len(pl) == 0:
                    continue
                pl = pl[0]

                vote = votes[pl.id]
                vote.Own = vote.Own + 1

            case C.Events.SUB:
                _player_in = U.clean_name(event['in'])
                _player_out = U.clean_name(event['out'])
                pl_in = player.Player.objects.filter(Surname=_player_in)
                pl_out = player.Player.objects.filter(Surname=_player_out)
                if len(pl_in) == 0 or len(pl_out) == 0:
                    continue
                pl_in = pl_in[0]
                pl_out = pl_out[0]

                vote_in = votes[pl_in.id]
                vote_out = votes[pl_out.id]
                vote_in.Sub = int(event['minute'])
                vote_out.Sub = int(event['minute']) * (-1)

def fill_live_votes(score, grades, live_votes):
    hlineup = score['home_lineups']
    hbench = score['home_bench']
    alineup = score['away_lineups']
    abench = score['away_bench']

    for p in hlineup:
        pl = player.Player.objects.filter(Surname=U.clean_name(p))
        if len(pl) == 0:
            continue
        pl = pl[0]
        _vote = vote.Vote.Vote_Obj()
        _vote.Player = pl

        if p in grades:
            _vote.Vote = float(grades[p])
            _vote.LiveStatus = C.LiveStatus.STARTING
        else:
            _vote.Vote = 6
            _vote.LiveStatus = C.LiveStatus.NOTHING
        live_votes[pl.id] = _vote

    for p in hbench:
        pl = player.Player.objects.filter(Surname=U.clean_name(p))
        if len(pl) == 0:
            continue
        pl = pl[0]
        _vote = vote.Vote.Vote_Obj()
        _vote.Player = pl        

        if p in grades:
            _vote.Vote = float(grades[p])
            _vote.LiveStatus = C.LiveStatus.NOTHING
        else:
            _vote.Vote = 6
            _vote.LiveStatus = C.LiveStatus.BENCH
        live_votes[pl.id] = _vote

    for p in alineup:
        pl = player.Player.objects.filter(Surname=U.clean_name(p))
        if len(pl) == 0:
            continue
        pl = pl[0]
        _vote = vote.Vote.Vote_Obj()
        _vote.Player = pl

        if p in grades:
            _vote.Vote = float(grades[p])
            _vote.LiveStatus = C.LiveStatus.STARTING
        else:
            _vote.Vote = 6
            _vote.LiveStatus = C.LiveStatus.NOTHING
        live_votes[pl.id] = _vote

    for p in abench:
        pl = player.Player.objects.filter(Surname=U.clean_name(p))
        if len(pl) == 0:
            continue
        pl = pl[0]
        _vote = vote.Vote.Vote_Obj()
        _vote.Player = pl

        if p in grades:
            _vote.Vote = float(grades[p])
            _vote.LiveStatus = C.LiveStatus.NOTHING
        else:
            _vote.Vote = 6
            _vote.LiveStatus = C.LiveStatus.BENCH
        live_votes[pl.id] = _vote

def get_live_votes(day, comp=1):
    TEST = False
    if(not TEST):
        url = "https://publicapi.fantamaster.it/livescores/?tcache=1756165942189"
        resp = req.get(url)
        resp_content = resp.content

        resp_json = json.loads(resp_content)
    else:
        f = open('l4m_app/scripts/live_parser/fake.json','r')
        resp_json = json.loads(f.read())
        f.close()

    live_votes = {}
    live_teams = []
    already_played_teams = []
    current_day = resp_json['day']
    grades = resp_json['marks']

    if (day != int(current_day)):
        return live_votes, live_teams, already_played_teams #empty

    for score in resp_json['scores']:
        
        d_start = datetime.datetime.strptime(score['rawdate'], '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Europe/Rome'))
        delta_start = datetime.timedelta(minutes=5) #start live 5 minutes before the match
        delta_end = datetime.timedelta(minutes=135) #stop live 135 minutes after the match

        isLive = d_start - delta_start < datetime.datetime.now(ZoneInfo('Europe/Rome')) < d_start + delta_end

        if(not isLive and d_start < datetime.datetime.now(ZoneInfo('Europe/Rome'))):
            already_played_teams.append(score['home_name'])
            already_played_teams.append(score['away_name'])

        if (not isLive):
            continue 
        
        match_events = score['events']

        live_teams.append(score['home_name'])
        live_teams.append(score['away_name'])
        
        fill_live_votes(score, grades, live_votes)
        fill_with_events(match_events, live_votes)

    for _, _vote in live_votes.items():
        _vote.Day = int(current_day)
        _vote.Competition = comp #TODO magic number: campionato

    return live_votes, live_teams, already_played_teams

def get_couples_and_matches_from_calendar(seriesid, day, competition_id=1):
    matches_ = matches_calendar.MatchesCalendar.objects.filter(
        # Q(CompetitionCalendar__Competition_id=competition_id) & 
        Q(CompetitionCalendar__Day=day) & 
        Q(Series_id=seriesid))
    couples = [(match.HomeTeam.id, match.AwayTeam.id, match.id) for match in matches_]
    return couples

def get_couples_from_calendar(seriesid, day, competition_id=1):
    matches_ = matches_calendar.MatchesCalendar.objects.filter(
        Q(CompetitionCalendar__Competition_id=competition_id) & 
        Q(CompetitionCalendar__Day=day) & 
        Q(Series_id=seriesid))
    couples = [(match.HomeTeam.id, match.AwayTeam.id) for match in matches_]
    return couples

def make_null_vote_obj(pl_id, cap_id=None):
    v_obj = vote.Vote.Vote_Obj()
    pl = player.Player.objects.get(pk=pl_id)
    v_obj.Player = pl if pl is not None else None
    if(pl_id == cap_id):
        v_obj.Cap = True
    v_obj.Vote = None
    v_obj.TotVote = None
    v_obj.Status = C.PlayerStatus.NO_PLAY_AT_ALL
    
    return v_obj

def make_empty_vote_obj(pl_id, cap_id, already_played, current_day):
    v_obj = vote.Vote.Vote_Obj()
    pl = player.Player.objects.get(pk=pl_id)
    v_obj.Player = pl if pl is not None else None
    if(pl_id == cap_id):
        v_obj.Cap = True
    v_obj.Vote = 6 if not already_played else None
    v_obj.TotVote = 6 if not already_played else None
    v_obj.Status = C.PlayerStatus.YET_TO_PLAY if not already_played else C.PlayerStatus.NOT_PLAYED
    real_match = real_calendar.Real_calendar.objects.filter(Q(Day=current_day) & \
                                                            (Q(RealTeamHome_id=pl.RealTeam) | Q(RealTeamAway_id=pl.RealTeam)))
    v_obj.Msg = real_match[0].Date.astimezone(ZoneInfo(key='Europe/Rome')).strftime('%d-%m-%Y alle %H:%M') if real_match else ""

    return v_obj

def make_not_called_vote_obj(pl_id, cap_id):
    v_obj = vote.Vote.Vote_Obj()
    pl = player.Player.objects.get(pk=pl_id)
    v_obj.Player = pl if pl is not None else None
    if(pl_id == cap_id):
        v_obj.Cap = True
    v_obj.Vote = 6
    v_obj.TotVote = 6
    v_obj.Status = C.PlayerStatus.PLAYING
    v_obj.LiveStatus = C.LiveStatus.NO_CALLED

    return v_obj

def adjust_vote_obj(_vote_obj, cap_id, empty=False):
    if(_vote_obj.Player.id == cap_id):
        _vote_obj.Cap = True
    _vote_obj.Status = C.PlayerStatus.PLAYING
    _vote_obj.Live = True
    if empty:
        _vote_obj.Vote = 6 
    _vote_obj.TotVote = calculate_total(_vote_obj) if not empty else 6
    
    return _vote_obj

def remake_items(mr):
    _items = []
    _items.append(mr.Home)
    _items.append(mr.Team.Name)
    _items.append(mr.PartialScore)
    _items.append(mr.ModifierVal)
    _items.append(mr.ModifierScore)
    _items.append(mr.BonusCap)
    _items.append(mr.BonusDisc)
    _items.append(mr.BonusPrest)
    _items.append(mr.Fp)
    _items.append(mr.NGoals)
    _items.append(mr.Module)
    _items.append(mr.OrigModule)
    _items.append(mr.ModNoGk)
    _items.append(mr.MissingSlots)
    _items.append(mr.Version)
    _items.append(mr.BonusHome)

    return _items

def remake_votes_obj(_votes):
    _votes_obj = []
    for _vote in _votes:
        v_obj = vote.Vote.Vote_Obj()
        v_obj.AssH = _vote['assh']
        v_obj.AssL = _vote['assl']
        v_obj.AssP = _vote['assp']
        v_obj.AssS = _vote['asss']
        v_obj.Player = player.Player.objects.get(pk=_vote['player'])
        v_obj.Day = _vote['day']
        v_obj.GoalDe = _vote['goalde']
        v_obj.GoalSc = _vote['goalsc']
        v_obj.GoalTa = _vote['goalta']
        v_obj.Own = _vote['own']
        v_obj.PenMi = _vote['penmi']
        v_obj.PenSa = _vote['pensa']
        v_obj.PenSc = _vote['pensc']
        v_obj.Red = _vote['red']
        v_obj.YelRed = _vote['yelred']
        v_obj.Sub = _vote['sub'] 
        v_obj.Status = C.PlayerStatus.PLAYED
        v_obj.SubJ = _vote['sub']
        v_obj.Yel = _vote['yel']
        v_obj.Vote = _vote['vote']
        v_obj.TotVote = _vote['totvote']
        v_obj.Cap = _vote['cap']
        v_obj.ChangedIn = _vote['changedin']
        v_obj.ChangedOut = _vote['changedout']
        v_obj.LiveStatus = _vote['livestatus']
        _votes_obj.append(v_obj)

    return _votes_obj

def make_vote_obj(_vote:vote.Vote, cap_id):
    v_obj = vote.Vote.Vote_Obj()
    v_obj.AssH = _vote.AssH
    v_obj.AssL = _vote.AssL
    v_obj.AssP = _vote.AssP
    v_obj.AssS = _vote.AssS
    v_obj.Player = _vote.Player
    v_obj.Competition = _vote.Competition
    v_obj.Day = _vote.Day
    v_obj.GoalDe = _vote.GoalDe
    v_obj.GoalSc = _vote.GoalSc
    v_obj.GoalTa = _vote.GoalTa
    v_obj.Own = _vote.Own
    v_obj.PenMi = _vote.PenMi
    v_obj.PenSa = _vote.PenSa
    v_obj.PenSc = _vote.PenSc
    v_obj.Red = _vote.Red
    v_obj.YelRed = _vote.YelRed
    v_obj.Sub = _vote.Sub 
    v_obj.Status = C.PlayerStatus.PLAYED #TODO
    v_obj.SubJ = _vote.SubJ
    v_obj.Yel = _vote.Yel
    v_obj.Vote = _vote.Vote
    v_obj.TotVote = calculate_total(_vote)
    if(_vote.Player_id == cap_id):
        v_obj.Cap = True
    v_obj.Status = C.PlayerStatus.PLAYED

    return v_obj

def calculate_total(v):
    sum = v.Vote

    sum += \
    (v.AssH * C.Scores.ASS_HIGH) + \
    (v.AssL * C.Scores.ASS_LOW) + \
    (v.AssP * C.Scores.PENALTY_PROCURED) + \
    (v.AssS * C.Scores.ASS_STD) + \
    (v.GoalDe * C.Scores.GOAL_DECIDER) + \
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

def calculate_modifier(gk_vote, def_votes, modNoGk):
    if(modNoGk):
        mod = statistics.mean(def_votes)
    else:
        mod = statistics.mean(sorted(def_votes)[1:] + gk_vote)
    
    ndef = len(def_votes)
    if mod < 6:
        return mod, (C.Modifier_Scores_4._LT_6 if ndef < 5 else C.Modifier_Scores_5._LT_6)
    if 6 <= mod < 6.25:
        return mod, (C.Modifier_Scores_4._6_625 if ndef < 5 else C.Modifier_Scores_5._6_625)
    if 6.25 <= mod < 6.5:
        return mod, (C.Modifier_Scores_4._625_65 if ndef < 5 else C.Modifier_Scores_5._625_65)
    if 6.5 <= mod < 6.75:
        return mod, (C.Modifier_Scores_4._65_675 if ndef < 5 else C.Modifier_Scores_5._65_675)
    if 6.75 <= mod < 7:
        return mod, (C.Modifier_Scores_4._675_7 if ndef < 5 else C.Modifier_Scores_5._675_7)
    if 7 <= mod < 7.5:
        return mod, (C.Modifier_Scores_4._7_75 if ndef < 5 else C.Modifier_Scores_5._7_75)
    if mod >= 7.5:
        return mod, (C.Modifier_Scores_4._GT_75 if ndef < 5 else C.Modifier_Scores_5._GT_75)
    
def calculate_n_goals(grand_total):
    diff = grand_total - C.Various.BASE_SCORE
    if (diff < 0):
        return 0
    
    return int(diff / C.Various.THRESHOLD_GOL) + 1

def check_already_played(real_team, already_played_teams, day):
    if int(U.get_current_day()) != day : #day yet to start, old json
        return True
    
    return real_team.Name in already_played_teams
    
def check_role_with_module(role_tit, role_ris, current_module):
    if(
        ((role_tit == 'D') and current_module in [C.Modules._343, C.Modules._352]) or \
        ((role_tit == 'C') and current_module in [C.Modules._433, C.Modules._532]) or \
        ((role_tit == 'A') and current_module in [C.Modules._541, C.Modules._451]) or \
        ((role_ris == 'D') and current_module in [C.Modules._532, C.Modules._541]) or \
        ((role_ris == 'C') and current_module in [C.Modules._352, C.Modules._451]) or \
        ((role_ris == 'A') and current_module in [C.Modules._343, C.Modules._433])
    ):    
        return False
    
    return True

def calculate_new_module(current_module, role_tit, role_ris):
    role_combo = (role_tit, role_ris)
    return C.Modules.matrix[current_module][role_combo]

def search_substitute(votes_ris, vote_tit, module):
    #TODO: check on max 5 substitutions
    good_statuses = [C.PlayerStatus.YET_TO_PLAY, C.PlayerStatus.PLAYING, C.PlayerStatus.PLAYED]
    same_role = [v for v in votes_ris if v.Player.Role == vote_tit.Player.Role 
                 and v.Status in good_statuses
                 and v.ChangedIn != ""]
    
    if len(same_role) > 0: #found
        same_role[0].ChangedIn = vote_tit.Player.Surname
        vote_tit.ChangedOut = same_role[0].Player.Surname
        return same_role[0], module
    else: #try other role, first player yet to play or with vote   
        for vote_ris in votes_ris:
            if(vote_ris.Status in good_statuses and 
               vote_tit.Player.Role != 'P' and
               vote_ris.Player.Role != 'P' and
               check_role_with_module(vote_tit.Player.Role, vote_ris.Player.Role, module)
               ):
                vote_ris.ChangedIn = vote_tit.Player.Surname
                vote_tit.ChangedOut = vote_ris.Player.Surname
                module = calculate_new_module(module, vote_tit.Player.Role, vote_ris.Player.Role)
                return vote_ris, module

    null_vote = make_null_vote_obj(vote_tit.Player.id)
    return null_vote, module

def check_valid_module_change_for_modifier(orig, current):
    if(orig == current): return True
    
    if(orig in [C.Modules._433, C.Modules._442, C.Modules._451] and 
       current in [C.Modules._433, C.Modules._442, C.Modules._451, C.Modules._532, C.Modules._541]):
        return True
    
    if(orig in [C.Modules._532, C.Modules._541] and 
       current in [C.Modules._532, C.Modules._541, C.Modules._433, C.Modules._442, C.Modules._451]):
        return True
    
    if(orig in [C.Modules._343, C.Modules._352]):
        return False

    #TODO: manage modifier change from 5 to 4

def isValid(vote):
    return (len(vote) > 0 and vote[0].Vote > 0)

def get_bonus_home(homeaway, home):
    if homeaway:
        return 1 if home else (-1)
    return 0

def get_votes(lineup, current_day, live_votes, live_teams, already_played_teams=[],\
               my_teamid = None, home=True, get_for_calculation=False, homeAway=False):
    votes_tit = []
    votes_ris = []
    module = C.Modules._442 #default
    _items = []

    if(type(lineup) is str): #NO SHOW
        _items.append("noshow")
        _items.append(lineup)
        return [votes_tit, _items, votes_ris] 

    _items.append(home)
    _items.append(lineup.Team.Name)

    day_already_started, _ = U.check_day_already_started(current_day)

    if(lineup.HideLineup and lineup.Team.id != my_teamid and not day_already_started): #HIDDEN LINEUP
        _items.append("hidden")
        _items.append(lineup)
        return [votes_tit, _items, votes_ris]

    line = json.loads(U.cleanJSON(lineup.Line))

    cap_id = line['captain'] if 'captain' in line.keys() else 0
    orig_module = line['mod'].replace('-','')
    cap_vote = 6

    for l in line.items(): #loop players in lineup
        if l[0] in ['captain', 'ot', 'penalties']:
            continue
        if(l[0] == 'mod'):  
            module = l[1].replace('-','')
            continue
        
        pl = player.Player.objects.get(pk=l[1])

        already_played = check_already_played(pl.RealTeam, already_played_teams, current_day) if not get_for_calculation else True

        #check if player is LIVE
        if pl.id in live_votes:
            _live_vote = live_votes[pl.id]
            if(l[0].endswith('tit')):
                votes_tit.append(adjust_vote_obj(_live_vote, cap_id) if _live_vote.Vote > 0 else \
                                adjust_vote_obj(_live_vote, cap_id, empty=True))
            else:
                votes_ris.append(adjust_vote_obj(_live_vote, cap_id) if _live_vote.Vote > 0 else \
                                adjust_vote_obj(_live_vote, cap_id, empty=True))

            if(pl.id == cap_id):
                cap_vote = _live_vote.Vote
        #CASE player not called
        elif(pl.id not in live_votes and pl.RealTeam.Name in live_teams):
            if(l[0].endswith('tit')):
                votes_tit.append(make_not_called_vote_obj(pl.id, cap_id))
            else:
                votes_ris.append(make_not_called_vote_obj(pl.id, cap_id))

            if(pl.id == cap_id):
                cap_vote = 6
        else:
        #player NOT LIVE
            _vote = vote.Vote.objects.filter(Q(Player_id=pl.id) & Q(Day=current_day))
            if(l[0].endswith('tit')):
                votes_tit.append(make_vote_obj(_vote[0], cap_id) if isValid(_vote) else \
                                make_empty_vote_obj(pl.id, cap_id, already_played, current_day))
            else:
                votes_ris.append(make_vote_obj(_vote[0], cap_id) if isValid(_vote) else \
                                make_empty_vote_obj(pl.id, cap_id, already_played, current_day))

            if len(_vote) > 0:
                if(pl.id == cap_id):
                    cap_vote = _vote[0].Vote
    
    valid_votes = []
    n_subs = 0
    ## get the valid votes ###################
    for vote_tit in votes_tit:
        if(vote_tit.Status == C.PlayerStatus.NOT_PLAYED):
            sub, module = search_substitute(votes_ris, vote_tit, module)
            if(module == 'KO'):
                return #here it should NEVER come
            if(sub.Status == C.PlayerStatus.NO_PLAY_AT_ALL): 
                vote_tit.Status = C.PlayerStatus.NO_PLAY_AT_ALL
            vote_tit.Vote = None
            vote_tit.TotVote = None

            if(sub.Status not in [C.PlayerStatus.NO_PLAY_AT_ALL]):
                if(n_subs == C.MAX_SUBS): #max 5 substitutions
                    continue
                n_subs = n_subs + 1
                valid_votes.append(sub)
                t_i = votes_tit.index(vote_tit)
                t_r = votes_ris.index(sub)
                votes_tit[t_i], votes_ris[t_r] = votes_ris[t_r], votes_tit[t_i] #swap

        elif(vote_tit.Status in [C.PlayerStatus.PLAYED, C.PlayerStatus.PLAYING, C.PlayerStatus.YET_TO_PLAY]):
            valid_votes.append(vote_tit)

    total = sum([v.TotVote for v in valid_votes])
    _items.append(total) 

    #modificatore
    def_votes = [v.Vote for v in valid_votes if v.Player.Role=='D']
    if (len(def_votes) >= 4 and check_valid_module_change_for_modifier(orig_module, module)): 
        gk_vote = [v.Vote for v in valid_votes if v.Player.Role=='P']
        val, modifier = calculate_modifier(gk_vote, def_votes, lineup.ModNoGk)
    else:
        val, modifier = 0 , 0

    _items.append(val)
    _items.append(modifier)

    #bonus capitano
    if cap_vote > 6:
        bonus_cap = 0.5
    elif cap_vote < 6:
        bonus_cap = -0.5
    else:
        bonus_cap = 0

    _noCards = len([v for v in valid_votes if (v.Red==1 or v.Yel==1 or v.YelRed==1)]) == 0
    _noBadVotes = len([v for v in valid_votes if v.Vote < 6]) == 0

    #bonus disciplina
    bonus_disc = 0.5 if _noCards else 0
    #bonus prestazioni
    bonus_prest = 0.5 if _noBadVotes else 0
    #bonus home
    bonus_home = get_bonus_home(homeAway, home)

    _items.append(bonus_cap)
    _items.append(bonus_disc)     
    _items.append(bonus_prest)     

    grand_total = total + modifier + bonus_cap + bonus_disc + bonus_prest + bonus_home
    _items.append(grand_total)

    # if get_for_calculation: #direct return for day calculation
    #     return grand_total

    n_goals = calculate_n_goals(grand_total)
    _items.append(n_goals)
    _items.append(module)
    if(orig_module != module):
        _items.append(orig_module)
    else:
        _items.append('same_module')
    _items.append(lineup.ModNoGk)
    _items.append(14 - len(votes_ris)) #missing slots
    _items.append(lineup.Version) #lineup version

    if homeAway:
        _items.append(1 if home else (-1))
    else:
        _items.append(0)

    votes_tit.sort(key=lambda vote:C.Constant_Dicts.RoleInts[vote.Player.Role])

    return [votes_tit, _items, votes_ris]
    
    
def enrich_and_sort_players(role, teamid, current_day, cap_id=-1, already_played_teams=[]):
    # needed by b11 (associates votes to pl, sorts by totvote and then vote)
    players = U.get_my_players_filtered(role, teamid)
    enriched_players = []

    for keep in players:
        idpl = keep["Player__id"]
        pl = player.Player.objects.get(pk=idpl)
        already_played = check_already_played(pl.RealTeam, already_played_teams, current_day)

        _vote = vote.Vote.objects.filter(Q(Player_id=idpl) & Q(Day=current_day))
        votes_pl = make_vote_obj(_vote[0], cap_id) if len(_vote) > 0 else \
                   make_empty_vote_obj(pl.id, cap_id, already_played, current_day)

        pl.votes = votes_pl
        enriched_players.append(pl)

    sorted_players = sorted(
        enriched_players,
        key=lambda p: (
            p.votes.TotVote if p.votes.TotVote is not None else -1,
            p.votes.Vote if p.votes.Vote is not None else -1
        ),
        reverse=True
    )

    return sorted_players



def pick_best_11(keepers, defenders, midfielders, attackers):
    best_lineup = None
    best_score = -1

    ALLOWED_MODULES = [
        (3, 4, 3),
        (3, 5, 2),
        (4, 3, 3),
        (4, 4, 2),
        (4, 5, 1),
        (5, 4, 1),
        (5, 3, 2),
    ]

    for d, m, a in ALLOWED_MODULES:
        try:
            # initial slice
            lineup = [keepers[0]] + defenders[:d] + midfielders[:m] + attackers[:a]

            # bench slice
            lineup_bench = keepers[1:] + defenders[d:] + midfielders[m:] + attackers[a:]
            
            ## --- Yellow-card swap ---
            #for i, p in enumerate(lineup):
            #    if getattr(p.votes, "YellowCard", False):
            #        if p.role == "P":
            #            role_list = keepers
            #        elif p.role == "D":
            #            role_list = defenders
            #        elif p.role == "C":
            #            role_list = midfielders
            #        else:
            #            role_list = attackers
			#
            #        for candidate in role_list:
            #            if (candidate.votes.TotVote == p.votes.TotVote and
            #                not getattr(candidate.votes, "YellowCard", False) and
            #                candidate not in lineup):
            #                lineup[i] = candidate
            #                break

            # sum TotVote
            score = sum((p.votes.TotVote or -1) for p in lineup)

            # modifier calc
            gk_vote = [keepers[0].votes.Vote] if keepers[0].votes.Vote is not None else []
            def_votes = [p.votes.Vote for p in defenders[:d] if p.votes.Vote is not None]

            if d > 3:
                mod_k, mod_score_k = calculate_modifier(gk_vote, def_votes, modNoGk=False)
                mod_nok, mod_score_nok = calculate_modifier(gk_vote, def_votes, modNoGk=True)
                mod, mod_score, modNoGk_used = max(
                    [(mod_k, mod_score_k, False), (mod_nok, mod_score_nok, True)],
                    key=lambda x: x[1]
                )
            else:
                mod, mod_score, modNoGk_used = 0., 0., False

            # score += mod_score

            # captain bonus
            captain = None
            bonus_cap = 0.
            for p in lineup:
                if p.votes.Vote is not None and p.votes.Vote > 6:
                    bonus_cap = 0.5
                    captain = p
                    break

            # all-six bonus
            bonus_six = 0.5 if all(p.votes.Vote is not None and p.votes.Vote >= 6 for p in lineup) else 0

            _noCards =  len([v for v in lineup if (v.votes.Red==1 or v.votes.Yel==1 or v.votes.YelRed==1)]) == 0
            no_yellow_bonus = 0.5 if _noCards else 0
            
            total_score = score + mod_score + bonus_cap + bonus_six + no_yellow_bonus
            if total_score > best_score:
                # info players
                players_list = []
                for p in lineup:
                    vote = p.votes.Vote
                    Tvote = p.votes.TotVote
                    players_list.append({
                        "player_id": p.id,
                        "player_rt": p.RealTeam,
                        "player_role": p.Role,
                        "player_surname": getattr(p, "surname", getattr(p, "name", str(p))),
                        "player_vote": vote,
                        "player_totvote": Tvote,
                        "player_stats": p.votes
                    })
                    
                for p in lineup_bench:
                    vote = p.votes.Vote
                    Tvote = p.votes.TotVote
                    players_list.append({
                        "player_id": p.id,
                        "player_rt": p.RealTeam,
                        "player_role": p.Role,
                        "player_surname": getattr(p, "surname", getattr(p, "name", str(p))),
                        "player_vote": vote,
                        "player_totvote": Tvote,
                        "player_stats": p.votes
                    })

                best_score = total_score
                best_lineup = {
                    "module": f"{d}{m}{a}",
                    "modif": mod_score,
                    "modif_tot": mod,
                    "players": players_list,
                    "modifier_from_no_gk": modNoGk_used,
                    "captain": captain,
                    "bcaptain": bonus_cap,
                    "all_six_bonus": bonus_six,
                    "no_yellow_bonus": no_yellow_bonus,
                    "score": total_score,
                    "partial_score": score
                }

        except IndexError:
            continue

    return best_lineup
