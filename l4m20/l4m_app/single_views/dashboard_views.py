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

        # default_league_ranking = U.get_ranking(competition_id, series_id)
        
        params = {
            'my_competitions' : my_competitions,
        }
        
        return render(request, self.template_name, params)