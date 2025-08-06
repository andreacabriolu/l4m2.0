from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
#from django.db.models import Q
#
from .. import utilities as U
#from ..models import *
#from l4m20 import constants as C
#from ..libs import *

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
        print(players)
        context = {
            'team_name': tname,
            'players_json': json.dumps(players),
        }
        return render(request, self.template_name, context)


	
	
class SquadViewOld(LoginRequiredMixin, View):
    template_name = 'l4m/squad.html'

    def get(self,request):
        
        user_team = U.get_user_team(request.user.id)
        tname = user_team['Name']
        tid = user_team['id']
		#for role in roles:
        keep = U.get_my_players('P', tid)
        #print(keep[0])
		#print(players_by_role)
        data = {
          'tname': tname,
          'keep': list(keep)[0]
        }
        print(json.dumps(data))

        return render(request, self.template_name, {'data_json': json.dumps(data)})
		#roles = ['POR', 'DIF', 'CEN', 'ATT']  
		#players_by_role = {}
		#
		#return render(request, self.template_name, {
		#	'players_by_role': players_by_role
		#})
