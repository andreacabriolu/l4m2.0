from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from .. import utilities as U
from ..models import *
from l4m20 import constants as C

class AuctionView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/auction.html'
    login_url = '/login/'

    def get(self,request):
        user_team = U.get_user_team(request.user.id)
        teamid = user_team['id']

        players_gk = U.get_players("P", teamid)
        players_def = U.get_players("D", teamid)
        players_cc = U.get_players("C", teamid)
        players_fw = U.get_players("A", teamid)

        my_best_bets = U.list_my_best_bets(U.get_my_best_bets(teamid))

        balance = U.get_balance(teamid)[0] #TODO: filter by season/league

        params = { 
            'user_team': user_team,
            'players_gk':players_gk,
            'players_def':players_def,
            'players_cc':players_cc,
            'players_fw':players_fw,
            'my_best_bets':my_best_bets,
            'balance' : balance,
          }
        
        return render(request, self.template_name, params)
    
class SendBetView(View):
    template_name = 'l4m/auction.html'

    def post(self, request): 
        try:
            data = json.loads(request.POST.get("jsonData"))
            if (data is None): return
            
            bal = U.send_bet(data)
            bal.save()
        except:
            return HttpResponse('error inserting bet and updating balance')
        
        return HttpResponse(json.dumps({'new_bal' : bal.Purchases_amount}))

class FinBetView(View):
    template_name = 'l4m/auction.html'

    def post(self, request): 
        try:
            data = json.loads(request.POST.get("jsonData"))
            if (data is None): return
            
            msg = U.finalize_bet(data)

            return HttpResponse(msg)
        except:
            return HttpResponse('error inserting bet and updating balance')

    
class GetPlayerInfoView(View):

    def post(self, request):
        id = request.POST.get("id")

        pl = player.Player.objects.\
        values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date','bet__Team_id__Name').\
        get(pk=id)

        pl_obj = json.dumps({'Sur':pl['Surname'], 
                             'Nam':pl['Name'], 
                             'Rol':pl['Role'],
                             'RealT':pl['RealTeam__Name'], 
                             'BetA':pl['bet__Amount'],
                             'BetE': pl['bet__Expiration_Date'][:-6], #remove final timestamp
                             'BetT': pl['bet__Team_id__Name']})

        return HttpResponse(pl_obj)

class GetBalanceView(View):
    def post(self,request):
        user_team = team.Team.objects.filter(Users__id=request.user.id).values('id')[0]
        
        return HttpResponse(U.get_balance(user_team['id'])['Purchases_amount']) #TODO: filter by season/league

def complete_list(l, num_max, role):
    if(len(l) < num_max):
        for _ in range(num_max - len(l)):
            l.append({"id": "-1", "Role":role})
    
    return l

class AllAuctionsView(LoginRequiredMixin, View):
    template_name = 'l4m/allauctions.html'

    def get(self,request):
        all_team_players = U.get_all_team_players()
        team_ids = team.Team.objects.all().values('id','Name')
        user_team_name = U.get_user_team(request.user.id)['Name'].replace(' ','_')
        team_players = {}

        for team_id in team_ids:
            lp = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['POR'])))
            ld = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['DIF'])))
            lc = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['CC'])))
            la = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['ATT'])))

            lp = complete_list(lp, C.NUM_GK, C.Constant_Dicts.RoleChars['POR'])
            ld = complete_list(ld, C.NUM_DEF, C.Constant_Dicts.RoleChars['DIF'])
            lc = complete_list(lc, C.NUM_CC, C.Constant_Dicts.RoleChars['CC'])
            la = complete_list(la, C.NUM_FW, C.Constant_Dicts.RoleChars['ATT'])

            team_players[team_id['Name'].replace(' ','_')] = lp + ld + lc + la
            
        team_players={user_team_name:team_players.pop(user_team_name), **team_players} #get user team as first

        params = { 
            'team_players' : json.dumps(team_players)
          }
        
        return render(request, self.template_name, params)
