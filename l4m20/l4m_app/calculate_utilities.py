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
        fp_home = _vote[0][1]
        fp_away = _vote[1][1]
        goal_home = U.calculate_n_goals(fp_home)
        goal_away = U.calculate_n_goals(fp_away)
        result = 'h' if goal_home > goal_away else 'a' if goal_away > goal_home else 'n'

        if(not noLineup):
            WIN_PT_H, DRAW_PT_H, LOSE_PT_H = U.check_penalties(team_home, day)
            WIN_PT_A, DRAW_PT_A, LOSE_PT_A = U.check_penalties(team_away, day)

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
    days = U.get_days(competition.id)
    days_to_calculate = sorted([d['Day'] for d in days if d['Day'] <= int(curr_day)]) if (int(day) < int(curr_day)) else [int(curr_day)]
    homeAway=U.get_homeaway(competition.id, day)

    for _day in days_to_calculate:
        if _day == int(curr_day): #arrow anti pattern...
            if not U.is_current_day_completed(): 
                continue

        for series in comp_series:
            series_teams = team.Team.objects.filter(Series__id=series.id)

            last_lineups_d = {}
            all_votes = []    

            for t in series_teams:
                lineup_to_show = LU.get_b11_lineup(t, _day)
                lineup_to_show['t']=t
                last_lineups_d[t.id] = lineup_to_show

            couples = LU.get_couples_and_matches_from_calendar(series.id, day, competition_id=competition.id)
            lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]], c[2]) for c in couples ]

            all_votes = []

            for lineup_couple in lineup_couples:

                fp_home = lineup_couple[0]['score'] + LU.get_bonus_home(homeaway=homeAway, home=True)
                fp_away = lineup_couple[1]['score'] + LU.get_bonus_home(homeaway=homeAway, home=False)

                all_votes.append( [[lineup_couple[0]['t'].id, fp_home], 
                                   [lineup_couple[1]['t'].id, fp_away], 
                                   lineup_couple[2]] )
        
            all_votes_per_series[series.id] = all_votes

        for k, vote_per_series in all_votes_per_series.items():
            save_results_for_total(vote_per_series) 
            write_league_rankings(vote_per_series, competition.id, _day, seriesid=k, noLineup=True)

def calculate_b11_league(competition, day):
    b11_series = U.get_unica_series(competition)
    if len(b11_series) > 0: 
        team_ids_names = team.Team.objects.values_list("id", "Name")

        curr_day = U.get_current_day() 
        days_to_calculate = range(int(day), int(curr_day)) if (int(day) < int(curr_day)) else [int(curr_day)]
        
        for _day in days_to_calculate:
            all_best = LU.get_best_11(team_ids_names, _day)
            write_b11_ranking(all_best, competition.id, b11_series[0].id, _day)

def calculate_league(competition, day):
    all_votes_per_series = {}
    comp_series = U.get_all_series(competition.id)

    curr_day = U.get_current_day() 
    days_to_calculate = range(int(day), int(curr_day)) if (int(day) < int(curr_day)) else [int(curr_day)]
    homeAway=U.get_homeaway(competition.id, day)

    for _day in days_to_calculate:
        for series in comp_series:
            series_teams = team.Team.objects.filter(Series__id=series.id)

            last_lineups_d = {}
            all_votes = []

            for t in series_teams:
                l = U.get_last_lineup(t, _day, comp_id=competition.id)

                lineup_to_show = l[0]
                last_lineups_d[t.id] = lineup_to_show

            couples = LU.get_couples_and_matches_from_calendar(series.id, _day, competition_id=competition.id)
            lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]], c[2]) for c in couples ]

            for lineup_couple in lineup_couples:
                votes_home = LU.get_votes(lineup_couple[0], _day, live_votes=[], live_teams=[], get_for_calculation=True, homeAway=homeAway)
                votes_away = LU.get_votes(lineup_couple[1], _day, live_votes=[], live_teams=[], get_for_calculation=True, homeAway=homeAway, home=False if homeAway else None)
                all_votes.append( [[lineup_couple[0].Team.id, votes_home], [lineup_couple[1].Team.id, votes_away], lineup_couple[2]] )

            all_votes_per_series[series.id] = all_votes
        
        for k, vote_per_series in all_votes_per_series.items():
            save_results(vote_per_series) 
            write_league_rankings(vote_per_series, competition.id, _day, seriesid=k)

def save_results(votes_per_series):

    for _votes in votes_per_series:
        home_results = _votes[0]
        away_results = _votes[1]
        mc = matches_calendar.MatchesCalendar.objects.get(pk=_votes[2])
        if mc is None:
            continue
        t1 = team.Team.objects.get(pk=home_results[0])
        t2 = team.Team.objects.get(pk=away_results[0])

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

def save_results_for_total(votes_per_series):

    for _votes in votes_per_series:
        home_results = _votes[0]
        away_results = _votes[1]
        mc = matches_calendar.MatchesCalendar.objects.get(pk=_votes[2])
        if mc is None:
            continue

        t1 = team.Team.objects.get(pk=home_results[0])
        t2 = team.Team.objects.get(pk=away_results[0])
        
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