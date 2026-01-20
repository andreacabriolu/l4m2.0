from .models import *
import json
from . import utilities as U
from . import live_utilities as LU
from django.db.models import Q
from l4m20 import constants as C

def write_league_rankings(vote_per_series, competition_id, day, seriesid, noLineup=False):
    last_ranking = U.get_last_available_ranking_by_day(competition_id, seriesid, int(day))
    
    if(last_ranking is not None):
        last_ranking = json.loads(last_ranking[0].RankingLine)
    
    new_ranking_line = []

    days = len([d for d in U.get_days(competition_id) if d['Day'] <= int(day)])

    WIN_PT_H = C.WIN_PT 
    WIN_PT_A = C.WIN_PT
    DRAW_PT_H = C.DRAW_PT
    DRAW_PT_A = C.DRAW_PT
    LOSE_PT_H = C.LOSE_PT
    LOSE_PT_A = C.LOSE_PT

    for _vote in vote_per_series:
        team_home = _vote[0][0]
        team_away = _vote[1][0]
        fp_home = _vote[0][1][1][8] #VERY BAD, but useful for rendering
        fp_away = _vote[1][1][1][8] #VERY BAD, but useful for rendering
        goal_home = U.calculate_n_goals(fp_home)
        goal_away = U.calculate_n_goals(fp_away)
        result = 'h' if goal_home > goal_away else 'a' if goal_away > goal_home else 'n'

        if(not noLineup):
            WIN_PT_H, DRAW_PT_H, LOSE_PT_H = U.check_penalties(team_home, day, competition_id)
            WIN_PT_A, DRAW_PT_A, LOSE_PT_A = U.check_penalties(team_away, day, competition_id)

        if(last_ranking is None): #match 1
            n_win_home = 1 if result == 'h' else 0
            n_null_home = 1 if result == 'n' else 0
            n_lose_home = 1 if result == 'a' else 0
            n_win_away = 1 if result == 'a' else 0
            n_null_away = 1 if result == 'n' else 0
            n_lose_away = 1 if result == 'h' else 0
            gf_home = goal_home
            gs_home = goal_away
            gf_away = goal_away
            gs_away = goal_home
            pt_home = WIN_PT_H if result == 'h' else DRAW_PT_H if result == 'n' else LOSE_PT_H
            pt_away = WIN_PT_A if result == 'a' else DRAW_PT_A if result == 'n' else LOSE_PT_A
            dr_home = gf_home - gs_home
            dr_away = gf_away - gs_away
        else:
            last_ranking_home = [item[team_home.__str__()] for item in last_ranking if team_home.__str__() in item] #QUITE BAD
            last_ranking_away = [item[team_away.__str__()] for item in last_ranking if team_away.__str__() in item] #QUITE BAD
            if len(last_ranking_home) == 0 or len(last_ranking_away) == 0:
                continue
            else:
                last_ranking_home = last_ranking_home[0]
                last_ranking_away = last_ranking_away[0]
            n_win_home = last_ranking_home['v'] + 1 if result == 'h' else last_ranking_home['v']
            n_null_home = last_ranking_home['n'] + 1 if result == 'n' else last_ranking_home['n']
            n_lose_home = last_ranking_home['p'] + 1 if result == 'a' else last_ranking_home['p']
            n_win_away = last_ranking_away['v'] + 1 if result == 'a' else last_ranking_away['v']
            n_null_away = last_ranking_away['n'] + 1 if result == 'n' else last_ranking_away['n']
            n_lose_away = last_ranking_away['p'] + 1 if result == 'h' else last_ranking_away['p']
            gf_home = last_ranking_home['gf'] + goal_home
            gs_home = last_ranking_home['gs'] + goal_away
            gf_away = last_ranking_away['gf'] + goal_away
            gs_away = last_ranking_away['gs'] + goal_home
            pt_home = last_ranking_home['pt'] + WIN_PT_H if result == 'h' else last_ranking_home['pt'] + DRAW_PT_H if result == 'n' else last_ranking_home['pt'] + LOSE_PT_H
            pt_away = last_ranking_away['pt'] + WIN_PT_A if result == 'a' else last_ranking_away['pt'] + DRAW_PT_A if result == 'n' else last_ranking_away['pt'] + LOSE_PT_A
            fp_home = last_ranking_home['fpt'] + fp_home
            fp_away = last_ranking_away['fpt'] + fp_away
            dr_home = gf_home - gs_home
            dr_away = gf_away - gs_away

        stats_home = {'pt': pt_home, 'fpt': fp_home, 'pg': days, 'v': n_win_home, 'n': n_null_home, 'p': n_lose_home, 'gf': gf_home, 'gs': gs_home, 'dr': dr_home}
        stats_away = {'pt': pt_away, 'fpt': fp_away, 'pg': days, 'v': n_win_away, 'n': n_null_away, 'p': n_lose_away, 'gf': gf_away, 'gs': gs_away, 'dr': dr_away}

        new_ranking_line_home = {team_home: stats_home}
        new_ranking_line_away = {team_away: stats_away}
        new_ranking_line.append(new_ranking_line_home)
        new_ranking_line.append(new_ranking_line_away)

    existing_rank = ranking.Ranking.objects.filter(Q(Day=day) & Q(Competition=competition_id) & Q(Series=seriesid))
    if len(existing_rank) > 0:
        existing_rank[0].delete()

    new_rank = ranking.Ranking(
        RankingLine = json.dumps(new_ranking_line),
        Competition = competition.Competition.objects.get(pk=competition_id),
        Series = series.Series.objects.get(pk=seriesid),
        Season = "SEASON 1", #TODO: season mechanism to do
        Day= day
    )
        
    new_rank.save()

def write_b11_ranking(all_best, competition_id, seriesid, day):
    last_ranking = U.get_ranking(competition_id, seriesid, int(day)-1)

    if(last_ranking is not None):
        last_ranking = json.loads(last_ranking[0].RankingLine)

    new_ranking_line = {}

    if(last_ranking is None): #match 1
        for best in all_best:
            if best is not None:
                new_ranking_line[best['team_id']] = best['score']
    else:
        for best in all_best:
            if best is not None:
                new_ranking_line[best['team_id']] = last_ranking[best['team_id'].__str__()] + best['score']

    existing_rank = ranking.Ranking.objects.filter(Q(Day=day) & Q(Competition=competition_id) & Q(Series=seriesid))
    if len(existing_rank) > 0:
        existing_rank[0].delete()

    new_rank = ranking.Ranking(
        RankingLine = json.dumps(new_ranking_line),
        Competition = competition.Competition.objects.get(pk=competition_id),
        Series = series.Series.objects.get(pk=seriesid),
        Season = "SEASON 1", #TODO: season mechanism to do
        Day= day
    )
        
    new_rank.save()

def calculate_total_league(competition, day):
    all_votes_per_series = {}
    comp_series = U.get_all_series(competition.id)
    curr_day = U.get_current_day() 
    all_league_days = U.get_days(competition.id)
    league_days = sorted([d['Day'] for d in all_league_days if int(day) <= d['Day'] <= int(curr_day)])
    days_to_calculate = league_days if (int(day) < int(curr_day)) else [int(curr_day)]

    for _day in days_to_calculate:
        if _day not in league_days:
            continue
        homeAway=U.get_homeaway(competition.id, day)
        for series in comp_series:
            series_teams = team.Team.objects.filter(Series__id=series.id)

            last_lineups_d = {}
            all_votes = []    

            for t in series_teams:
                lineup_to_show = LU.get_b11_lineup(t, _day, live_votes=[], live_teams=[], already_played_teams=[], getForCalculation=True)
                lineup_to_show['t']=t
                last_lineups_d[t.id] = lineup_to_show

            couples = LU.get_couples_and_matches_from_calendar(series.id, _day, competition_id=competition.id)
            lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]], c[2]) for c in couples ]

            all_votes = []

            for lineup_couple in lineup_couples:

                votes_home = LU.get_votes_total(lineup_couple[0], home=True, homeAway=homeAway)
                votes_away = LU.get_votes_total(lineup_couple[1], home=False, homeAway=homeAway)

                is_et, (home_agg, away_agg) = LU.check_match_for_extratime(lineup_couple[0]['t'].id, lineup_couple[1]['t'].id, 
                                                 votes_home, votes_away, 
                                                 day, competition.id)
                
                if(is_et): #extratime needed
                    extra_goals_home, extra_score_home, extra_votes_map_home = \
                        LU.calculate_extratime_goals_total(lineup_couple[0])
                    extra_goals_away, extra_score_away, extra_votes_map_away = \
                        LU.calculate_extratime_goals_total(lineup_couple[1])
                    
                    penalties_results = {}

                    votes_home[1][9] += extra_goals_home #BAD TODO use dict, please
                    votes_away[1][9] += extra_goals_away #BAD

                    if extra_goals_home == extra_goals_away:
                        penalties_results = \
                            LU.calculate_penalties_votes_total(lineup_couple[0], lineup_couple[1])
                        
                        pen_score_home = penalties_results.get('score_home', 0)
                        pen_score_away = penalties_results.get('score_away', 0)

                        # votes_home[1][9] += pen_score_home #BAD TODO use dict, please
                        # votes_away[1][9] += pen_score_away #BAD TODO use dict, please
                        if pen_score_home == pen_score_away:
                            pass #DRAW EVEN AFTER PENALTIES, CHECK FP IN THE TWO MATCHES (manual at the moment)

                    votes_home += ({'extratime': 
                                       {'et_result': json.dumps(
                                           {'results': extra_votes_map_home,
                                            'ngoals': extra_goals_home,
                                            'score': extra_score_home})
                                            }},)  #extratime home
                    votes_away += ({'extratime': 
                                       {'et_result': json.dumps(
                                           {'results': extra_votes_map_away,
                                            'ngoals': extra_goals_away,
                                            'score': extra_score_away})
                                            }},)  #extratime away
                    votes_home += ({'penalties': 
                                       {'pen_result': json.dumps(
                                            {'results': penalties_results.get('pen_results_home', {}), 
                                            'gk_opponent_surname': votes_away[0][0].Player.Surname,
                                            'gk_opponent_vote': votes_away[0][0].Vote}),
                                        'pen_score': penalties_results.get('score_home', 0),
                                                      }},)  #penalties home
                    votes_away += ({'penalties': 
                                       {'pen_result': json.dumps(
                                           {'results': penalties_results.get('pen_results_away', {}), 
                                            'gk_opponent_surname': votes_home[0][0].Player.Surname,
                                            'gk_opponent_vote': votes_home[0][0].Vote}),
                                        'pen_score': penalties_results.get('score_away', 0),
                                                      }},)  #penalties away

                all_votes.append( [[lineup_couple[0]['t'].id, votes_home], 
                                   [lineup_couple[1]['t'].id, votes_away], 
                                   lineup_couple[2],
                                   (home_agg, away_agg)] )
        
            all_votes_per_series[series.id] = all_votes

        for k, vote_per_series in all_votes_per_series.items():
            save_results(vote_per_series) 
            write_league_rankings(vote_per_series, competition.id, _day, seriesid=k, noLineup=True)

def calculate_b11_league(competition, day):
    b11_series = U.get_unica_series(competition)
    if len(b11_series) > 0: 
        team_ids_names = team.Team.objects.values_list("id", "Name")

        curr_day = U.get_current_day() 
        days_to_calculate = range(int(day), int(curr_day)) if (int(day) < int(curr_day)) else [int(curr_day)]
        
        for _day in days_to_calculate:
            all_best = LU.get_best_11(team_ids_names, _day, live_teams=[], live_votes=[], already_played_teams=[], getForCalculation=True)
            save_b11_results(all_best, _day)
            write_b11_ranking(all_best, competition.id, b11_series[0].id, _day)

def calculate_league(competition, day):
    all_votes_per_series = {}
    comp_series = U.get_all_series_from_calendar(competition.id, int(day))
    curr_day = U.get_current_day() 
    all_league_days = U.get_days(competition.id)
    league_days = sorted([d['Day'] for d in all_league_days if int(day) <= d['Day'] <= int(curr_day)])
    days_to_calculate = league_days if (int(day) < int(curr_day)) else [int(curr_day)]

    for _day in days_to_calculate:
        if _day not in league_days:
            continue
        all_votes_per_series = {}
        homeAway=U.get_homeaway(competition.id, _day)

        for series in comp_series:
            series_teams = team.Team.objects.filter(Series__id=series.id)

            last_lineups_d = {}
            all_votes = []

            for t in series_teams:
                l = U.get_last_lineup(t, _day, comp_id=competition.id) #BUG fixed

                if len(l) <= 0:
                    continue 

                lineup_to_show = l[0]
                last_lineups_d[t.id] = lineup_to_show

            if not last_lineups_d: continue #no valid lineup, current day still not available, skipping

            couples = LU.get_couples_and_matches_from_calendar(series.id, _day, competition_id=competition.id)
            lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]], c[2]) for c in couples ]

            for lineup_couple in lineup_couples:
                votes_home = LU.get_votes(lineup_couple[0], _day, live_votes=[], live_teams=[], get_for_calculation=True, homeAway=homeAway)
                votes_away = LU.get_votes(lineup_couple[1], _day, live_votes=[], live_teams=[], get_for_calculation=True, homeAway=homeAway, home=False if homeAway else None)
                
                is_et, (home_agg, away_agg) = LU.check_match_for_extratime(lineup_couple[0].Team.id, lineup_couple[1].Team.id, 
                                                 votes_home, votes_away, 
                                                 day, competition.id)

                if(is_et): #extratime needed
                    extra_goals_home, extra_score_home, extra_votes_map_home = \
                        LU.calculate_extratime_goals(votes_home, lineup_couple[0])
                    extra_goals_away, extra_score_away, extra_votes_map_away = \
                        LU.calculate_extratime_goals(votes_away, lineup_couple[1])
                    
                    penalties_results = {}

                    votes_home[1][9] += extra_goals_home #BAD TODO use dict, please
                    votes_away[1][9] += extra_goals_away #BAD
                    
                    if extra_goals_home == extra_goals_away:
                        penalties_results = \
                            LU.calculate_penalties_votes(lineup_couple[0], lineup_couple[1], votes_home, votes_away)
                        
                        pen_score_home = penalties_results.get('score_home', 0)
                        pen_score_away = penalties_results.get('score_away', 0)

                        # votes_home[1][9] += pen_score_home #BAD TODO use dict, please
                        # votes_away[1][9] += pen_score_away #BAD TODO use dict, please

                        if pen_score_home == pen_score_away:
                            pass #DRAW EVEN AFTER PENALTIES, CHECK FP IN THE TWO MATCHES (manual at the moment)

                    votes_home.append({'extratime': 
                                       {'et_result': json.dumps(
                                           {'results': extra_votes_map_home,
                                            'ngoals': extra_goals_home,
                                            'score': extra_score_home})
                                            }})  #extratime home
                    votes_away.append({'extratime': 
                                       {'et_result': json.dumps(
                                           {'results': extra_votes_map_away,
                                            'ngoals': extra_goals_away,
                                            'score': extra_score_away})
                                            }})  #extratime away
                    votes_home.append({'penalties': 
                                       {'pen_result': json.dumps(
                                            {'results': penalties_results.get('pen_results_home', {}), 
                                            'gk_opponent_surname': votes_away[0][0].Player.Surname,
                                            'gk_opponent_vote': votes_away[0][0].Vote}),
                                        'pen_score': penalties_results.get('score_home', 0),
                                                      }})  #penalties home
                    votes_away.append({'penalties': 
                                       {'pen_result': json.dumps(
                                           {'results': penalties_results.get('pen_results_away', {}), 
                                            'gk_opponent_surname': votes_home[0][0].Player.Surname,
                                            'gk_opponent_vote': votes_home[0][0].Vote}),
                                        'pen_score': penalties_results.get('score_away', 0),
                                                      }})  #penalties away
                
                all_votes.append( [[lineup_couple[0].Team.id, votes_home], [lineup_couple[1].Team.id, votes_away], lineup_couple[2], (home_agg, away_agg)])

            all_votes_per_series[series.id] = all_votes
        
        if not all_votes_per_series: continue
        for k, vote_per_series in all_votes_per_series.items():
            save_results(vote_per_series) 
            write_league_rankings(vote_per_series, competition.id, _day, seriesid=k)

def save_b11_results(all_best, day):
    for best in all_best:
        if best is not None: #RECALCULATE
            existing_b11 = b11_results.B11Results.objects.filter(Q(Day=day) & Q(Team__id=best['team_id']))
            if len(existing_b11) > 0:
                existing_b11[0].delete()

            b11_result = b11_results.B11Results(
                Day = day,
                Team = team.Team.objects.get(pk=best['team_id']),
                B11Fp = best['score']
            )
            
            b11_result.save()

def save_results(votes_per_series):

    for _votes in votes_per_series:
        home_results = _votes[0]
        away_results = _votes[1]
        mc = matches_calendar.MatchesCalendar.objects.get(pk=_votes[2])
        if mc is None:
            continue
        agg_scores = _votes[3] if len(_votes) > 3 else (None, None)
        home_team_id = home_results[0]
        away_team_id = away_results[0]
        t1 = team.Team.objects.get(pk=home_team_id)
        t2 = team.Team.objects.get(pk=away_team_id)

        #RECALCULATE?
        existing_mr_home = matches_results.MatchesResults.objects.filter(Q(Team=t1) & Q(MatchesCalendar=mc))
        existing_mr_away = matches_results.MatchesResults.objects.filter(Q(Team=t2) & Q(MatchesCalendar=mc))
        if len(existing_mr_home) > 0:
            existing_mr_home[0].delete()
        if len(existing_mr_away) > 0:
            existing_mr_away[0].delete()

        #ALL DATA
        home_team_data = home_results[1]
        home_team_items = home_team_data[1]
        home_data = {
            'votes_tit': [hd.todict() for hd in home_team_data[0]],
            'votes_ris': [hd.todict() for hd in home_team_data[2]],
            'fp': home_team_items[8],
            'home': home_team_items[0],
            'partial_score': home_team_items[2],
            'modifier_val': home_team_items[3],
            'modifier_score': home_team_items[4],
            'bonus_cap': home_team_items[5],
            'bonus_disc': home_team_items[6],
            'bonus_prest': home_team_items[7],
            'ngoals': home_team_items[9],
            'module': home_team_items[10],
            'orig_module': home_team_items[11],
            'modnogk': home_team_items[12],
            'missing_slots': home_team_items[13],
            'version': home_team_items[14],
            'bonus_home': home_team_items[15],
            'pen': 1 if home_team_items[14] < 0 else 0,
            'fpo': json.loads(home_team_data[3]['extratime']['et_result'])['score'] if len(home_team_data) > 3 else None,
            'extratime': home_team_data[3]['extratime']['et_result'] if len(home_team_data) > 3 else None,
            'penalties': home_team_data[4]['penalties']['pen_result'] if len(home_team_data) > 4 else None,
        }

        away_team_data = away_results[1]
        away_team_items = away_team_data[1]
        away_data = {
            'votes_tit': [ad.todict() for ad in away_team_data[0]],
            'votes_ris': [ad.todict() for ad in away_team_data[2]],
            'fp': away_team_items[8],
            'home': away_team_items[0],
            'partial_score': away_team_items[2],
            'modifier_val': away_team_items[3],
            'modifier_score': away_team_items[4],
            'bonus_cap': away_team_items[5],
            'bonus_disc': away_team_items[6],
            'bonus_prest': away_team_items[7],
            'ngoals': away_team_items[9],
            'module': away_team_items[10],
            'orig_module': away_team_items[11],
            'modnogk': away_team_items[12],
            'missing_slots': away_team_items[13],
            'version': away_team_items[14],
            'bonus_home': away_team_items[15],
            'pen': 1 if away_team_items[14] < 0 else 0 ,
            'fpo': json.loads(away_team_data[3]['extratime']['et_result'])['score'] if len(away_team_data) > 3 else None,
            'extratime': away_team_data[3]['extratime']['et_result'] if len(away_team_data) > 3 else None,
            'penalties': away_team_data[4]['penalties']['pen_result'] if len(away_team_data) > 4 else None,
        }

        mr_home = matches_results.MatchesResults(Team = t1, 
                                              Fp = home_data['fp'], 
                                              Votes_Tit = home_data['votes_tit'], 
                                              Votes_Ris = home_data['votes_ris'], 
                                              Home = home_data['home'], 
                                              PartialScore = home_data['partial_score'], 
                                              ModifierVal = home_data['modifier_val'], 
                                              ModifierScore = home_data['modifier_score'], 
                                              BonusCap = home_data['bonus_cap'], 
                                              BonusDisc = home_data['bonus_disc'], 
                                              BonusPrest = home_data['bonus_prest'], 
                                              NGoals = home_data['ngoals'], 
                                              Module = home_data['module'], 
                                              OrigModule = home_data['orig_module'], 
                                              ModNoGk = home_data['modnogk'], 
                                              MissingSlots = home_data['missing_slots'], 
                                              Version = home_data['version'], 
                                              BonusHome = home_data['bonus_home'], 
                                              Pen = home_data['pen'],
                                              FpO = home_data['fpo'],
                                              ExtraTimePlayers = home_data['extratime'],
                                              PenaltyPlayers = home_data['penalties'],
                                              AggregateScore = agg_scores[0] if agg_scores else None,
                                              MatchesCalendar = mc)

        mr_away = matches_results.MatchesResults(Team = t2, 
                                                Fp = away_data['fp'], 
                                                Votes_Tit = away_data['votes_tit'], 
                                                Votes_Ris = away_data['votes_ris'], 
                                                Home = away_data['home'], 
                                                PartialScore = away_data['partial_score'], 
                                                ModifierVal = away_data['modifier_val'], 
                                                ModifierScore = away_data['modifier_score'], 
                                                BonusCap = away_data['bonus_cap'], 
                                                BonusDisc = away_data['bonus_disc'], 
                                                BonusPrest = away_data['bonus_prest'], 
                                                NGoals = away_data['ngoals'], 
                                                Module = away_data['module'], 
                                                OrigModule = away_data['orig_module'], 
                                                ModNoGk = away_data['modnogk'], 
                                                MissingSlots = away_data['missing_slots'], 
                                                Version = away_data['version'], 
                                                BonusHome = away_data['bonus_home'],
                                                Pen = away_data['pen'],
                                                FpO = away_data['fpo'],
                                                ExtraTimePlayers = away_data['extratime'],
                                                PenaltyPlayers = away_data['penalties'],
                                                AggregateScore = agg_scores[1] if agg_scores else None,
                                                MatchesCalendar = mc)
        
        mr_home.save()
        mr_away.save()

def save_results_for_total(votes_per_series):

    for _votes in votes_per_series:
        home_results = _votes[0]
        away_results = _votes[1]
        mc = matches_calendar.MatchesCalendar.objects.get(pk=_votes[2])
        if mc is None:
            continue
        home_team_id = home_results[0]
        away_team_id = away_results[0]
        t1 = team.Team.objects.get(pk=home_team_id)
        t2 = team.Team.objects.get(pk=away_team_id)
        
        #RECALCULATE?
        existing_mr_home = matches_results.MatchesResults.objects.filter(Q(Team=t1) & Q(MatchesCalendar=mc))
        existing_mr_away = matches_results.MatchesResults.objects.filter(Q(Team=t2) & Q(MatchesCalendar=mc))
        if len(existing_mr_home) > 0:
            existing_mr_home[0].delete()
        if len(existing_mr_away) > 0:
            existing_mr_away[0].delete()

        mr_home = matches_results.MatchesResults(Team = t1, 
                                              Fp = home_results[1],
                                              MatchesCalendar = mc)

        mr_away = matches_results.MatchesResults(Team = t2, 
                                              Fp = away_results[1],
                                              MatchesCalendar = mc)
        
        mr_home.save()
        mr_away.save()