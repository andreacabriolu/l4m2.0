from .models import *
import json
from . import utilities as U
from . import live_utilities as LU


def write_b11_ranking(all_best, competition_id, seriesid, day):
    last_ranking = U.get_ranking(competition_id, seriesid, int(day)-1)

    if(last_ranking is not None):
        last_ranking = json.loads(last_ranking[0].RankingLine)

    new_ranking_line = []

    if(last_ranking is None): #match 1
        for best in all_best:
            if best is not None:
                new_ranking_line.append({best['team_id']:best['score']})
    else:
        pass


    new_rank = ranking.Ranking(
        RankingLine = json.dumps(new_ranking_line),
        Competition = competition.Competition.objects.get(pk=competition_id),
        Series = series.Series.objects.get(pk=seriesid),
        Season = "SEASON 1", #TODO: season mechanism to do
        Day= day
    )
        
    new_rank.save()

def calculate_b11_league(competition, day):
    b11_series = U.get_unica_series(competition)
    if len(b11_series) > 0: 
        team_ids_names = team.Team.objects.values_list("id", "Name")
        all_best = LU.get_best_11(team_ids_names, day)
        write_b11_ranking(all_best, competition.id, b11_series[0].id, day)

def calculate_main_league(competition, day):
    all_votes_per_series = {}
    comp_series = U.get_all_series(competition.id)
    for series in comp_series:
        series_teams = team.Team.objects.filter(Series__id=series.id)

        last_lineups_d = {}
        all_votes = []

        for t in series_teams:
            l = U.get_last_lineup(t, day)
            last_valid_l = U.get_last_valid_lineup(t) #TODO: manage last valid lineup for a day

            lineup_to_show = l[0]
            last_lineups_d[t.id] = lineup_to_show

        couples = LU.get_couples_and_matches_from_calendar(series.id, day)
        lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]], c[2]) for c in couples ]

        for lineup_couple in lineup_couples:
            votes_home = LU.get_votes(lineup_couple[0], day, live_votes=[], live_teams=[], get_for_calculation=True)
            votes_away = LU.get_votes(lineup_couple[1], day, live_votes=[], live_teams=[], get_for_calculation=True)
            all_votes.append( [[lineup_couple[0].Team.id, votes_home], [lineup_couple[1].Team.id, votes_away], lineup_couple[2]] )

        all_votes_per_series[series.id] = all_votes
    
    for k, vote_per_series in all_votes_per_series.items():
        U.save_results(vote_per_series) 
        U.write_main_league_rankings(vote_per_series, competition.id, day, seriesid=k)