from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from .. import utilities as U
from ..models import *
from l4m20 import constants as C
from ..libs import *


class SquadView(LoginRequiredMixin, View):
    template_name = 'l4m/squad.html'

    def get(self,request):
        all_team_players = U.get_all_team_players()
        team_ids = team.Team.objects.all().values('id','Name')
        user_team_name = U.get_user_team(request.user.id)['Name'].replace(' ','_')
        team_players = {}
        balances = {}

        for team_id in team_ids:
            lp = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['POR'])))
            ld = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['DIF'])))
            lc = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['CC'])))
            la = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['ATT'])))

            lp = U.complete_list(lp, C.NUM_GK, C.Constant_Dicts.RoleChars['POR'])
            ld = U.complete_list(ld, C.NUM_DEF, C.Constant_Dicts.RoleChars['DIF'])
            lc = U.complete_list(lc, C.NUM_CC, C.Constant_Dicts.RoleChars['CC'])
            la = U.complete_list(la, C.NUM_FW, C.Constant_Dicts.RoleChars['ATT'])

            team_players[team_id['Name'].replace(' ','_')] = lp + ld + lc + la
            
            #TODO: manage more than 1 balance!
            balance = U.get_balance(team_id['id'])
            if(not balance):
                continue
            balances[team_id['Name'].replace(' ','_')] = U.get_balance_for_bets(team_id['id'], balance[0]['Purchases_max'])
            
        team_players={user_team_name:team_players.pop(user_team_name), **team_players} #get user team as first

        params = { 
            'team_players' : json.dumps(team_players),
            'balances' : json.dumps(balances)
          }
        
        return render(request, self.template_name, params)
