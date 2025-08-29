from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q


from .. import utilities as U
from .. import live_utilities as LU
from ..models import *
from l4m20 import constants as C

class LiveB11View(LoginRequiredMixin, View):
    template_name = 'l4m/live_b11.html'

    def get(self, request):
        current_day = U.get_current_day()
        teamid = U.get_user_team(request.user.id)['id']

        team_ids_names = team.Team.objects.values_list("id", "Name")
        last_lineups_d = {}
        
        all_best = []

        # crea best 11 per ogni squadra
        for tid,name in team_ids_names:
            keepers = LU.enrich_and_sort_players('P', tid, current_day)
            defenders = LU.enrich_and_sort_players('D', tid, current_day)
            midfielders = LU.enrich_and_sort_players('C', tid, current_day)
            attackers = LU.enrich_and_sort_players('A', tid, current_day)
            best = LU.pick_best_11(keepers, defenders, midfielders, attackers)
            if(best):
                best["team_id"]=tid
                best["team_name"]=name
                                
            last_lineups_d[tid] = best
            all_best.append(best)

        sorted_best = sorted(
            (b for b in all_best if b is not None),
            key=lambda x: x['score'],
            reverse=True
        )
        
        params = {
            'sorted_best': sorted_best
        }

        return render(request, self.template_name, params)

def LiveView(request):
    template_name = 'l4m/live.html'

    teamid = U.get_user_team(request.user.id)['id']

    current_day = U.get_current_day()
    all_days = range(1, int(current_day) + 1)

    competition_id = 1 #DEFAULT campionato
    my_series = U.get_my_series(teamid, competitionid=competition_id)
    my_seriesid = my_series[0].id

    my_competitions = U.get_my_competitions(teamid, my_series)

    if(len(request.POST) > 0 and 'jsonData' in request.POST):
        data = json.loads(request.POST['jsonData'])
        seriesid = data['series']
        if(seriesid != my_seriesid):
            teamid = None
        day = int(data['day'])
    else:
        day = current_day
        seriesid = my_seriesid

    all_series = U.get_all_series(competitionid=competition_id) #TODO: magic number

    series_teams = team.Team.objects.filter(Series__id=seriesid)
    last_lineups_d = {}
    overtime, _ = U.check_day_already_started(day)

    for t in series_teams:
        l = U.get_last_lineup(t, day)
        if(len(l) <= 0 and overtime): #overtime
            last_valid_l = U.get_last_valid_lineup(t)
            #TODO: save lst valid lineup

        lineup_to_show = t.Name #base

        if not overtime:
            if len(l) > 0:
                lineup_to_show = l[0]
            else:
                lineup_to_show = t.Name

        if overtime and day == current_day:
            if len(last_valid_l) > 0:
                lineup_to_show = last_valid_l[0]
            else:
                lineup_to_show = t.Name
        else:  #filter for historical data
            lineup_to_show = l[0] if len(l)> 0 else t.Name #always valued because we SHOULD save the lineup


        last_lineups_d[t.id] = lineup_to_show

    couples = LU.get_couples_from_calendar(seriesid, day)
    couples = [couples.pop(couples.index(i)) for i in couples if (i[0]==teamid or i[1]==teamid)]+couples #get user match as first
    lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]]) for c in couples ]

    all_votes = []

    #get all live players
    live_votes = LU.get_live_votes(day)

    for lineup_couple in lineup_couples:
        votes_home = LU.get_votes(lineup_couple[0], day, live_votes, teamid)
        votes_away = LU.get_votes(lineup_couple[1], day, live_votes, teamid, home=False)
        all_votes.append( \
            [votes_home, votes_away]
        )
        
    params = { 
        'all_votes' : all_votes,
        'all_series' : all_series,
        'current_series' : seriesid,
        'all_days' : all_days,
        'current_day': day,
        'my_competitions' : my_competitions
        }
    
    return render(request, template_name, params)
    
