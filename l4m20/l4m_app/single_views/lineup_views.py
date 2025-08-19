from datetime import datetime
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

        players_gk = U.get_my_players_filtered("P", teamid)
        players_def = U.get_my_players_filtered("D", teamid)
        players_cc = U.get_my_players_filtered("C", teamid)
        players_fw = U.get_my_players_filtered("A", teamid)
        players_my = list(players_def) + list(players_cc)+ list(players_fw)
        players_all = players_my + list(players_gk)

        params = { 
            'mods': mods,
            'user_team': user_team,
            'players_gk':players_gk,
            'players_def':players_def,
            'players_cc':players_cc,
            'players_fw':players_fw,
            'players_my':players_my,
            'players_all':players_all
          }
        
        return render(request, self.template_name, params)
    
class SaveLineupView(View):
  def post(self, request):
    try:
        tits = request.POST['tits']
        options = request.POST['options']

        if (tits is None or options is None): return

        lineup = json.loads(tits)
        options = json.loads(options)

        last_version = 0
        day = U.get_current_day()
        teamid = U.get_user_team(request.user.id)['id']
        last_lineup = U.get_last_lineup(teamid, day)

        if(last_lineup):
            last_version = last_lineup[0].Version

        lineup_info = {
            "line": lineup,
            "day": day,
            "team": teamid,
            "version": last_version + 1,
            "timestamp": datetime.now(),
            "series": U.get_my_series(teamid)[0],
            "hideLineup": options['hideLineup'],
            "modNoGk": options['modNoGk'],
        }

        U.save_lineup(lineup_info)
        return HttpResponse("success")

    except Exception as e:
            return HttpResponse(f'error saving lineup: {e}') 
    
class GetLastLineupView(View):
    def get(self, request):

        try:
          last_lineup = U.get_last_lineup(U.get_user_team(request.user.id)['id'], U.get_current_day())
          if (not last_lineup):
              return HttpResponse("")
          else: 
              ret_json = json.dumps([last_lineup[0].Line, last_lineup[0].Timestamp.__str__(), 
                                     last_lineup[0].HideLineup, last_lineup[0].ModNoGk])
              return HttpResponse(U.cleanJSON(ret_json))        
        except Exception as e:
            return HttpResponse(f"error: {e}")