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
        my_team = U.get_user_team(request.user.id)
        my_series = U.get_my_series(teamid=my_team['id'])
        my_competitions = U.get_my_competitions(my_series)

        if len(my_series) <= 0 or len (my_competitions) <= 0:
            return HttpResponse('error: no series for the team')

        main_league = competition.Competition.objects.filter(Name='Campionato')
        main_league_day = U.get_current_day() #TODO: filter day per competition
        main_league_ranking = U.get_ranking(main_league[0], my_series[0], main_league_day)
        if(len(main_league_ranking) <= 0):
            return HttpResponse('error: no default ranking found')
        
        json_l = json.loads(main_league_ranking[0].RankingLine)
        lines = []
        for l in json_l:
            line = []
            for k,v in l.items():
                line.append(team.Team.objects.get(pk=k).Name)
                for _,_v in v.items():
                    line.append(int(_v)) 
            lines.append(line)



        params = {
            'my_competitions' : my_competitions,
            'main_league_ranking' : lines,
        }
        
        return render(request, self.template_name, params)