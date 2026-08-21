from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from .. import utilities as U
from l4m_app.models import player

class SquadView(LoginRequiredMixin, View):
    template_name = 'l4m/squad.html'

    def get(self, request):

        user_team = U.get_user_team(request.user.id)

        tid = user_team['id']
        tname = user_team['Name']
        series_mine = U.get_my_series(tid)
        myseries=series_mine[0].Name
        uname='-'

        
        # 1. Total count of players in DB
        print("Total Players:", player.Player.objects.count())
        
        # 2. Inspect all field names and foreign relations on the Player model
        print("\n--- PLAYER FIELDS & RELATIONS ---")
        for f in player.Player._meta.get_fields():
            print(f"{f.name} -> {f.get_internal_type() if hasattr(f, 'get_internal_type') else 'Relation'}")
                
        tinfo = {"team_name": tname,"team_series": myseries,"team_user":uname}
        
        players = list(U.get_my_players_filtered('P', tid))  # pass '' or modify to get all roles
        players += list(U.get_my_players_filtered('D', tid))  # pass '' or modify to get all roles
        players += list(U.get_my_players_filtered('C', tid))  # pass '' or modify to get all roles
        players += list(U.get_my_players_filtered('A', tid))  # pass '' or modify to get all roles

        context = {
            'tinfo_json': json.dumps(tinfo),
            'players_json': json.dumps(players),
        }
        

        return render(request, self.template_name, context)

