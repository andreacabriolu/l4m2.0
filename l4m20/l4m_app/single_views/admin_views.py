from datetime import datetime
from zoneinfo import ZoneInfo
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

class CalculateView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/calculate.html'

    def get(self,request):

        all_competitions = U.get_all_competitions()
        current_day = U.get_current_day() #TODO: per competition?
        
        params = {
            'all_competitions': all_competitions,
            'current_day': current_day,
        }
        
        return render(request, self.template_name, params)
    
class GetCurrentDayByCompetition(View):
    def post(self, request):
        #TODO: filter by competition!
        competition_id = request.POST['competitionid']
        c = competition.Competition.objects.get(pk=int(competition_id))
        if c is None:
            return HttpResponse('error: no competition found')

        current_day = U.get_current_day(c.Name)

        return HttpResponse(current_day)
    
class CalculateDayView(View):
    def post(self, request):

        #TODO: write in:
        # calendar (NEW)

        try:

            competitionid = request.POST['competitionid']
            day = request.POST['day']
            comp_series = U.get_all_series(competitionid)

            all_votes_per_series = {}
            
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
                #rankings
                U.write_main_league_rankings(vote_per_series, competitionid, day, seriesid=k)
            
            #b11 ranking calculation
            b11_comp = U.get_competition(name='b11')
            b11_series = U.get_unica_series(b11_comp)
            if len(b11_comp) > 0 and len(b11_series) > 0: 
                U.write_b11_ranking(competitionid=b11_comp[0].id, seriesid=b11_series[0].id, day=day)


            return HttpResponse('GIORNATA CALCOLATA')

        except Exception as e:
            return HttpResponse(f'error {e}')
        
class SetDayView(View):
    def post(self, request):
        c_day = request.POST['day']
        config_day = config.Config.objects.filter(Name="CurrentDay").first()
        config_day.Value = c_day
        config_day.save()

        return HttpResponse(c_day)
