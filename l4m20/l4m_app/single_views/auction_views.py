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

class AuctionView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/auction.html'
    login_url = '/login/'

    def get(self,request):
        try:
            user_team = U.get_user_team(request.user.id)
            teamid = user_team['id']

            players_gk = U.get_players("P", teamid)
            players_def = U.get_players("D", teamid)
            players_cc = U.get_players("C", teamid)
            players_fw = U.get_players("A", teamid)

            my_market = U.get_my_markets(U.get_my_series(teamid)[0].id)[0].id #TODO: improve check
            my_best_bets = U.list_my_best_bets(U.get_my_best_bets(teamid, my_market))

            balance = U.get_balance(teamid)[0] #TODO: improve check
            balance_for_bets = U.get_balance_for_bets(teamid, balance['Purchases_max'])
            if(balance_for_bets is None): 
                balance_for_bets = 0
            n_carognate = balance['N_carognate']

            params = { 
                'user_team': user_team,
                'players_gk':players_gk,
                'players_def':players_def,
                'players_cc':players_cc,
                'players_fw':players_fw,
                'my_best_bets':my_best_bets,
                'balance' : balance,
                'balance_for_bets' : balance_for_bets,
                'my_market': my_market,
                'max_carognate' : C.MAX_CAROGNATE,
                'n_carognate' : n_carognate
            }
        except Exception as e:
            raise Exception(f'{e}')
        
        return render(request, self.template_name, params)
    
class SendBetView(View):
    template_name = 'l4m/auction.html'

    def post(self, request): 
        uname = request.user.username

        try:
            data = json.loads(request.POST.get("jsonData"))
            if (data is None): return
            
            logger.debug(f"{uname} : SENDING BET: {data}")

            bet_result, balance_max, n_carognate = U.send_bet(data)

            if(bet_result == C.SendBetResult.BET_OVERFLOW):
                return HttpResponse(f'error PUNTATA TROPPO ALTA!')
        except Exception as e:
            return HttpResponse(f'error inserting bet and updating balance: {e}')
        
        return HttpResponse(json.dumps({'amount': bet_result, 'max': balance_max, 'n_carognate': n_carognate}))

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

        my_market = U.get_my_market(userid=request.user.id)

        pl = player.Player.objects.\
        filter(mark_players__Market_id=my_market.id).\
        values('id','Surname','Name','Role','RealTeam__Name','mark_players__bet__Amount','mark_players__bet__Expiration_Date',
               'mark_players__bet__Team_id__Name','mark_players__Market_id').\
        get(pk=id)

        pl_obj = json.dumps({'Sur':pl['Surname'], 
                             'Nam':pl['Name'], 
                             'Rol':pl['Role'],
                             'RealT':pl['RealTeam__Name'], 
                             'BetA':pl['mark_players__bet__Amount'],
                             'BetE': pl['mark_players__bet__Expiration_Date'][:-6] if pl['mark_players__bet__Expiration_Date'] != None else pl['mark_players__bet__Expiration_Date'], #remove final timestamp
                             'BetT': pl['mark_players__bet__Team_id__Name']})

        return HttpResponse(pl_obj)

class GetBalanceView(View):
    def post(self,request):
        user_team = team.Team.objects.filter(Users__id=request.user.id).values('id')[0]
        
        return HttpResponse(U.get_balance(user_team['id'])['Purchases_amount']) #TODO: filter by season/league
    
class GetBalanceForBetsView(View):
    def post(self, request):
        user_team = team.Team.objects.filter(Users__id=request.user.id).values('id')[0]

        return HttpResponse(
                U.get_balance_for_bets(user_team['id'], 
                U.get_balance(user_team['id'])[0]['Purchases_max']))


class AllAuctionsView(LoginRequiredMixin, View):
    template_name = 'l4m/allauctions.html'

    def get(self,request,series_id=None):

        user_team = U.get_user_team(request.user.id)
        teamid = user_team['id']
        series_mine = U.get_my_series(teamid)
        myseries=series_mine[0].id
                
        if series_id is None:
          user_team = U.get_user_team(request.user.id)
          teamid = user_team['id']
          series_id = U.get_my_series(teamid)
          seriesid = series_id[0].id
        
        else:
          seriesid = series_id
         
         
        all_team_players = U.get_all_team_players()
        
        team_ids = team.Team.objects.all().values('id','Name')
        team_ids_to_filter = team.Team.objects.all().values('id','Name')
        filtered_teams = []
        for team_id in team_ids_to_filter:
            tid=team_id['id']
            foreign_series = U.get_my_series(tid)
            if foreign_series.exists():
               fsid = foreign_series[0].id
               if fsid == seriesid:
                   filtered_teams.append(team_id)
                   

        
        user_team_name = U.get_user_team(request.user.id)['Name'].replace(' ','_')
        team_players = {}
        balances = {}
        
        series_players = U.get_series_players(series_id) 
        

        for team_id in filtered_teams:
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
            
        if(seriesid == myseries):
            team_players={user_team_name:team_players.pop(user_team_name), **team_players} #get user team as first

        params = { 
            'team_players' : json.dumps(team_players),
            'balances' : json.dumps(balances)
          }
        
        return render(request, self.template_name, params)
