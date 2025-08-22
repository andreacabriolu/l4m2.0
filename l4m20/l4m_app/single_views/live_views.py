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

        team_ids = team.Team.objects.values_list("id", flat=True)
        last_lineups_d = {}

        # crea best 11 per ogni squadra
        for tid in team_ids:
            keepers = LU.enrich_and_sort_players('P', tid, current_day)
            defenders = LU.enrich_and_sort_players('D', tid, current_day)
            midfielders = LU.enrich_and_sort_players('C', tid, current_day)
            attackers = LU.enrich_and_sort_players('A', tid, current_day)
            best = LU.pick_best_11(keepers, defenders, midfielders, attackers)
            last_lineups_d[tid] = best
            


        all_votes = []

    
        params = {
            'all_votes': all_votes
        }

        return render(request, self.template_name, params)

class LiveView(LoginRequiredMixin, View):
    template_name = 'l4m/live.html'

    def get(self,request):
        current_day = U.get_current_day()
        teamid = U.get_user_team(request.user.id)['id']
        seriesid = U.get_my_series(teamid)[0].id                     
                               
        series_teams = team.Team.objects.filter(Series__id=seriesid)
        last_lineups_d = {}
        for t in series_teams:
            l = U.get_last_lineup(t, current_day)
            last_lineups_d[t.id] = l[0] if len(l) > 0 else t.Name #TODO: get last valid lineup

        last_lineups_d={teamid:last_lineups_d.pop(teamid), **last_lineups_d} #get user lineup as first

        couples = LU.get_couples_from_calendar(seriesid, current_day)
        lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]]) for c in couples ]

        all_votes = []

        for lineup_couple in lineup_couples:
            votes_home = LU.get_votes(lineup_couple[0], current_day, teamid)
            votes_away = LU.get_votes(lineup_couple[1], current_day, teamid, home=False)
            all_votes.append( \
                [votes_home, votes_away]
            )
        print(all_votes)    
        params = { 
            'all_votes' : all_votes,
          }
        
        return render(request, self.template_name, params)
    
