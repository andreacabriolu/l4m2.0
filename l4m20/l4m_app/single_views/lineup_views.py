from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from .. import utilities as U
from ..models import *
from l4m20 import constants as C

class LineupView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/lineup.html'

    def get(self,request):
        user_team = U.get_user_team(request.user.id)
        teamid = user_team['id']
        mods = C.Constant_Lists.Modules

        players_gk = U.get_my_players("P", teamid)
        players_def = U.get_my_players("D", teamid)
        players_cc = U.get_my_players("C", teamid)
        players_fw = U.get_my_players("A", teamid)

        params = { 
            'mods': mods,
            'user_team': user_team,
            'players_gk':players_gk,
            'players_def':players_def,
            'players_cc':players_cc,
            'players_fw':players_fw,
          }
        
        return render(request, self.template_name, params)
    
