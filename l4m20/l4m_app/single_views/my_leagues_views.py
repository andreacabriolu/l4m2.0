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
        my_series = U.get_my_series(my_team['id'], competition_id)
        all_series = U.get_all_series(competition_id)
        logo_path = comp.LogoPath
        day = U.get_current_day()

        params = {
            'comp' : comp,
            'my_series' : my_series.first() if my_series.exists() else None,
            'all_series' : all_series,
            'logo_path': logo_path,
            'day': day,
        }
        
        return render(request, self.template_name, params)