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

class MyLeaguesView(LoginRequiredMixin, View):
    template_name = 'l4m/my_leagues.html'

    def get(self,request, competition_id=None):
        my_team = U.get_user_team(request.user.id)
        comp = competition.Competition.objects.get(id=competition_id)
        logo_path = comp.LogoPath
        
        groups_data = U.get_groups_data_for_competition(competition_id)
        bracket_data = U.get_bracket_data_for_competition(competition_id)

        params = {
            'comp' : comp,
            'logo_path': logo_path,
            'current_stage': 'Girone', #TODO restore U.get_current_stage(competition_id),
            'groups_data': U.get_groups_data_for_competition(competition_id),
            'bracket_data': U.get_bracket_data_for_competition(competition_id),
        }
        
        return render(request, self.template_name, params)

class MyLeaguesNoMatchView(LoginRequiredMixin, View):
    template_name = 'l4m/my_leagues.html'

    def get(self,request, competition_id=None):
        my_team = U.get_user_team(request.user.id)
        comp = competition.Competition.objects.get(id=competition_id)
        logo_path = comp.LogoPath
        
        groups_data = U.get_groups_data_no_competition(competition_id)
        # ~ bracket_data = U.get_bracket_data_no_competition(competition_id)

        # ~ groups_data = U.get_groups_data_for_competition(competition_id)
        # ~ bracket_data = U.get_bracket_data_for_competition(competition_id)

        params = {
            'comp' : comp,
            'logo_path': logo_path,
            'current_stage': 'Girone', #TODO restore U.get_current_stage(competition_id),
            'groups_data': U.get_groups_data_for_competition(competition_id),
            'bracket_data': U.get_bracket_data_for_competition(competition_id),
        }
        
        return render(request, self.template_name, params)
    
class RetrieveCalendarInfoView(View):
    def get(self, request):
        series_id = request.GET['s_id']
        day = request.GET['day']
        calendar_entries = U.get_results_calendar(series_id, day)

        if calendar_entries is None:
            return HttpResponse(json.dumps({ 'calendarlines': [] }))

        return HttpResponse(json.dumps({ 'calendarlines': calendar_entries }))
