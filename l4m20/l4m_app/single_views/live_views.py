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
        
        print(sorted_best)
        
        params = {
            'sorted_best': sorted_best
        }

        return render(request, self.template_name, params)

class LiveView(LoginRequiredMixin, View):
def LiveView(request):
    template_name = 'l4m/live.html'

    current_day = U.get_current_day()
    all_series = U.get_all_series(competitionid=1) #TODO: magic number
    teamid = U.get_user_team(request.user.id)['id']
    
    my_seriesid = U.get_my_series(teamid)[0].id
    if(len(request.POST) > 0 and 'jsonData' in request.POST):
        seriesid = int(request.POST['jsonData'])
        if(seriesid != my_seriesid):
            teamid = None
    else:
        seriesid = my_seriesid

    series_teams = team.Team.objects.filter(Series__id=seriesid)
    last_lineups_d = {}
    for t in series_teams:
        l = U.get_last_lineup(t, current_day)
        last_lineups_d[t.id] = l[0] if len(l) > 0 else t.Name #TODO: get last valid lineup

    couples = LU.get_couples_from_calendar(seriesid, current_day)
    couples = [couples.pop(couples.index(i)) for i in couples if (i[0]==teamid or i[1]==teamid)]+couples #get user match as first
    lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]]) for c in couples ]

    all_votes = []

    for lineup_couple in lineup_couples:
        votes_home = LU.get_votes(lineup_couple[0], current_day, teamid)
        votes_away = LU.get_votes(lineup_couple[1], current_day, teamid, home=False)
        all_votes.append( \
            [votes_home, votes_away]
        )
        
    params = { 
        'all_votes' : all_votes,
        'all_series' : all_series,
        'current_series' : seriesid
        }
    
    return render(request, template_name, params)
    
