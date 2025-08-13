from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import datetime
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
            seriesid=U.get_my_series(teamid)[0].id
            
            filtered_teams = team.Team.objects.filter(Series__id=seriesid)
            filtered_teams_ids = [team.id for team in filtered_teams]
            
            players_gk = U.get_players_my_series("P", teamid, filtered_teams_ids)
            players_def = U.get_players_my_series("D", teamid, filtered_teams_ids)
            players_cc = U.get_players_my_series("C", teamid, filtered_teams_ids)
            players_fw = U.get_players_my_series("A", teamid, filtered_teams_ids)

            my_market = U.get_my_markets(seriesid)[0].id #TODO: improve check
            my_best_bets = U.list_my_best_bets(U.get_my_best_bets(teamid, my_market))
            current_session = U.get_current_session(my_market)

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
                'residual': balance['Purchases_max'] - U.get_current_bets_amount(teamid),
                'my_market': my_market,
                'session': current_session,
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
            
            if(bet_result == C.SendBetResult.BET_UNDERFLOW):
                return HttpResponse(f'error PUNTATA TROPPO BASSA!')

            if(bet_result == C.SendBetResult.BET_EXPIRED):
                return HttpResponse(f'error GIOCATORE SCADUTO!')
            
            if(bet_result == C.SendBetResult.BET_SLOT_EXCEED):
                return HttpResponse(f'error NUMERO MASSIMO DI GIOCATORI PER RUOLO!')

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
            filter(bet__Market_id=my_market).\
            values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date',
               'bet__Team_id__Name').\
            get(pk=id)

        pl_obj = json.dumps({'Sur':pl['Surname'], 
                             'Nam':pl['Name'], 
                             'Rol':pl['Role'],
                             'RealT':pl['RealTeam__Name'], 
                             'BetA':pl['bet__Amount'],
                             'BetE': datetime.datetime.strptime(pl['bet__Expiration_Date'], '%Y-%m-%d %H:%M:%S%z').\
                                replace(tzinfo=datetime.timezone.utc).__str__() if pl['bet__Expiration_Date'] != None else pl['bet__Expiration_Date'], #remove final timestamp
                             'BetT': pl['bet__Team_id__Name']})

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

    def get(self,request):

        user_team = U.get_user_team(request.user.id)
        teamid = user_team['id']
    
        seriesid = U.get_my_series(teamid)
        all_team_players = U.get_all_team_players()
        filtered_teams = team.Team.objects.filter(Series__id=seriesid)
        
        user_team_name = U.get_user_team(request.user.id)['Name'].replace(' ','_')
        team_players = {}
        balances = {}
        
        for team_id in filtered_teams:
            lp = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['POR'])))
            ld = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['DIF'])))
            lc = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['CC'])))
            la = list(all_team_players.filter(Q(bet__Team_id=team_id['id']) & Q(Role=C.Constant_Dicts.RoleChars['ATT'])))
            
            balances_ = U.get_balance(team_id['id'])
            if len(balances_) <= 0: 
                continue

            balance = balances_[0]
            balance_for_bets = U.get_balance_for_bets(team_id['id'], balance['Purchases_max'])
            
            amount = balance['Purchases_max']
            pmax = balance_for_bets
            current_bets_amount = U.get_current_bets_amount(team_id['id'])

            li = [{'Surname': 'Monte Acquisti', 'Name': None, 'bet__Team_id': team_id['id'], 'bet__Amount': amount, 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Restante', 'Name': None, 'bet__Team_id': team_id['id'], 'bet__Amount': (amount - current_bets_amount), 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Puntata Massima', 'Name': None, 'bet__Team_id': team_id['id'], 'bet__Amount': pmax, 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Carognate', 'Name': None, 'bet__Team_id': team_id['id'], 'bet__Amount': balance['N_carognate'], 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  ]
            
            lp = U.complete_list(lp, C.NUM_GK, C.Constant_Dicts.RoleChars['POR'])
            ld = U.complete_list(ld, C.NUM_DEF, C.Constant_Dicts.RoleChars['DIF'])
            lc = U.complete_list(lc, C.NUM_CC, C.Constant_Dicts.RoleChars['CC'])
            la = U.complete_list(la, C.NUM_FW, C.Constant_Dicts.RoleChars['ATT'])

            team_players[team_id['Name'].replace(' ','_')] = lp + ld + lc + la + li

            # #TODO: manage more than 1 balance!
            # balance = U.get_balance(team_id['id'])
            # if(not balance):
            #     continue
            balances[team_id['Name'].replace(' ','_')] = U.get_balance_for_bets(team_id['id'], balance['Purchases_max'])
            
         
        filtered_team_ids = {team['id'] for team in filtered_teams}
        

        team_players = {
            team_name: [p for p in players if p.get('bet__Team_id') in filtered_team_ids]
            for team_name, players in team_players.items()
        }     
        
        team_players={user_team_name:team_players.pop(user_team_name), **team_players} #get user team as first

        params = { 
            'team_players' : json.dumps(team_players),
            'balances' : json.dumps(balances)
          }
        
        return render(request, self.template_name, params)
