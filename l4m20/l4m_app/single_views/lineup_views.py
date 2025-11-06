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

class LineupView(View):
    def get(self, request):
        pass
    def post(self, request):
        pass

def LineupView_(request):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/lineup.html'

    user_team = U.get_user_team(request.user.id)
    teamid = user_team['id']
    mods = C.Constant_Lists.Modules
    current_day = U.get_current_day()
    my_series = U.get_all_my_series(teamid)

    day_already_started, day_time_limit = U.check_day_already_started(current_day)
    
    players_gk = U.get_my_players_filtered("P", teamid)
    players_def = U.get_my_players_filtered("D", teamid)
    players_cc = U.get_my_players_filtered("C", teamid)
    players_fw = U.get_my_players_filtered("A", teamid)

    for gk in players_gk:
        pl_realteamid = gk['Player__RealTeam__id']
        real_match = real_calendar.Real_calendar.objects.filter(Q(Day=current_day) & \
                                                        (Q(RealTeamHome_id=pl_realteamid) | Q(RealTeamAway_id=pl_realteamid)))
        if(len(real_match) <= 0):
            continue
        gk['played'] = datetime.now(ZoneInfo('Europe/Rome')) >= real_match[0].Date.astimezone(ZoneInfo(key='Europe/Rome'))
        gk['vs'] = f'{real_match[0].RealTeamHome.Name[:3]}-{real_match[0].RealTeamAway.Name[:3]}'

    for df in players_def:
        pl_realteamid = df['Player__RealTeam__id']
        real_match = real_calendar.Real_calendar.objects.filter(Q(Day=current_day) & \
                                                        (Q(RealTeamHome_id=pl_realteamid) | Q(RealTeamAway_id=pl_realteamid)))
        if(len(real_match) <= 0):
            continue
        df['played'] = datetime.now(ZoneInfo('Europe/Rome')) >= real_match[0].Date.astimezone(ZoneInfo(key='Europe/Rome'))
        df['vs'] = f'{real_match[0].RealTeamHome.Name[:3]}-{real_match[0].RealTeamAway.Name[:3]}'

    for cc in players_cc:
        pl_realteamid = cc['Player__RealTeam__id']
        real_match = real_calendar.Real_calendar.objects.filter(Q(Day=current_day) & \
                                                        (Q(RealTeamHome_id=pl_realteamid) | Q(RealTeamAway_id=pl_realteamid)))
        if(len(real_match) <= 0):
            continue
        cc['played'] = datetime.now(ZoneInfo('Europe/Rome')) >= real_match[0].Date.astimezone(ZoneInfo(key='Europe/Rome'))
        cc['vs'] = f'{real_match[0].RealTeamHome.Name[:3]}-{real_match[0].RealTeamAway.Name[:3]}'

    for fw in players_fw:
        pl_realteamid = fw['Player__RealTeam__id']
        real_match = real_calendar.Real_calendar.objects.filter(Q(Day=current_day) & \
                                                        (Q(RealTeamHome_id=pl_realteamid) | Q(RealTeamAway_id=pl_realteamid)))
        if(len(real_match) <= 0):
            continue
        fw['played'] = datetime.now(ZoneInfo('Europe/Rome')) >= real_match[0].Date.astimezone(ZoneInfo(key='Europe/Rome'))
        fw['vs'] = f'{real_match[0].RealTeamHome.Name[:3]}-{real_match[0].RealTeamAway.Name[:3]}'

    players_my = list(players_def) + list(players_cc)+ list(players_fw)
    players_all = players_my + list(players_gk)
    all_competitions = U.get_my_lineup_active_competitions(my_series)

    if(len(request.POST) > 0 and 'jsonData' in request.POST):
        data = json.loads(request.POST['jsonData'])
        competition_id = data['competition']
    else:
        competition_id=1
    
    params = { 
        'mods': mods,
        'user_team': user_team,
        'players_gk':players_gk,
        'players_def':players_def,
        'players_cc':players_cc,
        'players_fw':players_fw,
        'players_my':players_my,
        'players_all':players_all,
        'day_time_limit':day_time_limit.strftime('%d-%m-%Y alle %H:%M'),
        'day_already_started': day_already_started,
        'all_competitions': all_competitions,
        'competition_id': competition_id,
        }
    
    return render(request, template_name, params)

class SaveMultipleLineupView(View):
    def post(self, request):
        try:
            tits = request.POST['tits']
            options = request.POST['options']
            all_comp_ids = request.POST['all_comp_ids']

            if (tits is None or options is None): return

            all_comp_ids = json.loads(all_comp_ids)
            lineup = json.loads(tits)
            options = json.loads(options)
            day = U.get_current_day()
            teamid = U.get_user_team(request.user.id)['id']

            for single_comp_id in all_comp_ids:
                last_version = 0
                last_lineup = U.get_last_lineup(teamid, day, single_comp_id)

                if(last_lineup):
                    last_version = last_lineup[0].Version if last_lineup[0].Version != (-1) else 0

                lineup_info = {
                    "line": lineup,
                    "day": day,
                    "team": teamid,
                    "version": last_version + 1,
                    "timestamp": datetime.now(),
                    "series": U.get_my_series(teamid, competitionid=single_comp_id)[0],
                    "hideLineup": options['hideLineup'],
                    "modNoGk": options['modNoGk'],
                }

                U.save_lineup(lineup_info)

            return HttpResponse("success")

        except Exception as e:
                return HttpResponse(f'error saving lineup: {e}') 
    
class SaveLineupView(View):
  def post(self, request):
    try:
        tits = request.POST['tits']
        options = request.POST['options']
        comp_id = request.POST['comp_id']

        if (tits is None or options is None): return

        lineup = json.loads(tits)
        options = json.loads(options)

        last_version = 0
        day = U.get_current_day()
        teamid = U.get_user_team(request.user.id)['id']
        last_lineup = U.get_last_lineup(teamid, day, comp_id)

        if(last_lineup):
            last_version = last_lineup[0].Version if last_lineup[0].Version != (-1) else 0

        lineup_info = {
            "line": lineup,
            "day": day,
            "team": teamid,
            "version": last_version + 1,
            "timestamp": datetime.now(),
            "series": U.get_my_series(teamid, competitionid=comp_id)[0],
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
          comp_id = request.GET['comp']
          last_lineup = U.get_last_lineup(U.get_user_team(request.user.id)['id'], U.get_current_day(), comp_id)
          if (not last_lineup):
              return HttpResponse("")
          else: 
              ret_json = json.dumps([last_lineup[0].Line, last_lineup[0].Timestamp.__str__(), 
                                     last_lineup[0].HideLineup, last_lineup[0].ModNoGk])
              return HttpResponse(U.cleanJSON(ret_json))        
        except Exception as e:
            return HttpResponse(f"error: {e}")