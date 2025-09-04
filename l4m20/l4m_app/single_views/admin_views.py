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

class CalculateView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/calculate.html'

    def get(self,request):

        all_competitions = U.get_all_competitions()
        

        
        params = {
            'all_competitions': all_competitions
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

        pass