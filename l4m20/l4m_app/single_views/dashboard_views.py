from datetime import datetime
from zoneinfo import ZoneInfo
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from .. import utilities as U
from ..models import *
from l4m20 import constants as C

class DashboardView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/dashboard.html'

    def get(self,request):
        main_league = competition.Competition.objects.filter(Name='Campionato')
        all_campionato_series = U.get_all_series(competitionid=main_league[0].id)

        my_team = U.get_user_team(request.user.id)
        my_series = U.get_my_series(teamid=my_team['id'])
        my_competitions = U.get_my_competitions(my_series)

        logo_path = my_team['LogoPath']

        if len(my_series) <= 0 or len (my_competitions) <= 0:
            return HttpResponse('error: no series for the team')

        # main_league_day = U.get_current_day() #TODO: filter day per competition
        # main_league_ranking = U.get_ranking(main_league[0], my_series[0], main_league_day)
        # if(len(main_league_ranking) <= 0):
        #     return HttpResponse('error: no default ranking found')

        params = {
            'my_competitions' : my_competitions,
            'main_league' : main_league[0],
            'my_main_league_series' : my_series[0],
            'day': U.get_current_day(),
            'all_campionato_series': all_campionato_series,
            'logo_path': logo_path,
        }
        
        return render(request, self.template_name, params)

class GetSeriesByCompetitionView(View):
    def post(self, request):
        c_id = request.POST['c_id']
        series = U.get_all_series(c_id)
        return HttpResponse(json.dumps([(s.id,s.Name) for s in series]))

class RetrieveRankingInfoView(View):
    def post(self, request):
        c_id = request.POST['c_id']
        s_id = request.POST['s_id']
        day = request.POST['day']
        
        _ranking = U.get_ranking(c_id, s_id, day)

        json_l = json.loads(_ranking[0].RankingLine)
        lines = []
        for l in json_l:
            line = []
            for k,v in l.items():
                line.append(team.Team.objects.get(pk=k).Name.upper())
                for _,_v in v.items():
                    line.append(int(_v)) 
            lines.append(line)

        return HttpResponse(json.dumps({ 'lines': lines }))
