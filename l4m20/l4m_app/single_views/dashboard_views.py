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
        my_series = U.get_all_my_series(teamid=my_team['id'])
        all_competitions = U.get_all_live_competitions()
        current_season = U.get_current_season()

        logo_path = my_team['LogoPath']

        if len(my_series) <= 0 or len (all_competitions) <= 0:
            return HttpResponse('error: no series for the team')

        params = {
            'my_competitions' : all_competitions,
            'main_league' : main_league[0],
            'my_main_league_series' : my_series[0],
            'day': U.get_current_day(),
            'all_campionato_series': all_campionato_series,
            'logo_path': logo_path,
            'season': current_season.Name,
        }
        
        return render(request, self.template_name, params)

class GetTeamSeriesByCompetitionView(View):
    def post(self, request):
        c_id = request.POST['c_id']
        t_name = request.POST['t_name']
        t_id = U.get_team_by_name(t_name)
        series = U.get_my_series(t_id, c_id)
        return HttpResponse(json.dumps([(s.id) for s in series]))


class GetSeriesByCompetitionView(View):
    def post(self, request):
        c_id = request.POST['c_id']
        series = U.get_all_series(c_id)
        return HttpResponse(json.dumps([(s.id,s.Name) for s in series]))
    
class GetDaysByCompetitionView(View):
    def get(self, request):
        c_id = request.GET['c_id']
        days = U.get_days(c_id)
        cd = U.get_current_day()
        return HttpResponse(json.dumps(sorted([d['Day'] for d in days if d['Day'] <= int(cd)], reverse=True)))

class RetrieveB11RankingInfoView(View):
    def post(self, request):
        day = request.POST['day']
        
        b11_comp = U.get_competition(name='Best 11')
        b11_series = U.get_unica_series(b11_comp[0].id)
        _ranking = U.get_ranking(b11_comp[0].id, b11_series[0].id, int(day) - 1)

        if(_ranking is None):
            return HttpResponse(json.dumps({ 'lines' : [None,None] }))

        json_l = json.loads(_ranking[0].RankingLine)
        lines = []
        for k,_v in json_l.items():
            line = []
            line.append(team.Team.objects.get(pk=k).Name.upper())
            line.append(int(_v))
            # _scores_fp= U.get_scores(k) TODO: save b11 results and print in the dashboard table
            # line.append(_scores_fp)
            lines.append(line)

        return HttpResponse(json.dumps({ 'lines': lines }))

class RetrieveRankingInfoView(View):
    def post(self, request):
        c_id = request.POST['c_id']
        s_id = request.POST['s_id']
        day = request.POST['day']
        
        _ranking = U.get_last_available_ranking(c_id, s_id)

        if(_ranking is None):
            return HttpResponse(json.dumps({ 'lines' : [None,None,None,None,None,None,None,None,None,None] }))

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
