from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from .. import utilities as U

class SquadView(LoginRequiredMixin, View):
    template_name = 'l4m/squad.html'

    def get(self, request):
        user_team = U.get_user_team(request.user.id)
        tid = user_team['id']
        tname = user_team['Name']

        # Get all players for the team, any role
        players = list(U.get_my_players('P', tid))  # pass '' or modify to get all roles
        players += list(U.get_my_players('D', tid))  # pass '' or modify to get all roles
        players += list(U.get_my_players('C', tid))  # pass '' or modify to get all roles
        players += list(U.get_my_players('A', tid))  # pass '' or modify to get all roles

        context = {
            'team_name': tname,
            'players_json': json.dumps(players),
        }
        return render(request, self.template_name, context)

