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
            
            # best 11 bit
            keep = LU.enrich_and_sort_players('P', t.id, current_day)
            difs = LU.enrich_and_sort_players('D', t.id, current_day)
            mids = LU.enrich_and_sort_players('C', t.id, current_day)
            atts = LU.enrich_and_sort_players('A', t.id, current_day)
            
            best = LU.pick_best_11(keep, difs, mids, atts)
            
            if(best):
              print("Team:", t.Name,"Best module:", best["module"], ", modif:", best["modif"], ", modif tot:", best["modif_tot"], ", modno_keep:", 
              best["modifier_from_no_gk"], ", captain:", best["captain"], ", all six:", best["all_six_bonus"], 
              ", no yell:", best["no_yellow_bonus"], ", score:", best["score"])
              for p in best["players"]:
                 print(p.Surname, p.votes.Vote, p.votes.TotVote)
            #####                       
        
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
            
        params = { 
            'all_votes' : all_votes,
          }
        
        return render(request, self.template_name, params)
    
