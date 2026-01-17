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
            my_market = U.get_my_markets(seriesid)[0].id #TODO: improve check
            my_best_bets = U.list_my_best_bets(U.get_my_best_bets(teamid, my_market))
            current_session = U.get_current_session(my_market)
            
            filtered_teams = team.Team.objects.filter(Series__id=seriesid)
            filtered_teams_ids = [team.id for team in filtered_teams]
            my_svincoli_current_session = U.get_my_svincolati(team=teamid, session=current_session)
            
            players_gk = U.get_players_my_series("P", teamid, filtered_teams_ids, my_svincoli_current_session)
            players_def = U.get_players_my_series("D", teamid, filtered_teams_ids, my_svincoli_current_session)
            players_cc = U.get_players_my_series("C", teamid, filtered_teams_ids, my_svincoli_current_session)
            players_fw = U.get_players_my_series("A", teamid, filtered_teams_ids, my_svincoli_current_session)

            free_players = list(players_gk) + list(players_def) + list(players_cc) + list(players_fw)

            balance = U.get_balance(teamid)[0] #TODO: improve check
            balance_for_bets = U.get_balance_for_bets(teamid, balance['Purchases_max'])
            if(balance_for_bets is None): 
                balance_for_bets = 0
            n_carognate = balance['N_carognate']
            n_svincoli = balance['N_svincoli']

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
                'n_carognate' : n_carognate,
                'max_svincoli' : C.MAX_SVINCOLI,
                'n_svincoli' : n_svincoli,
                'free_players' : free_players,
                'is_live_day': U.is_live_day()

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
            if(msg == C.ErrorCodes.ALREADY_OFFICIAL):
                return HttpResponse('error GIOCATORE GIÀ UFFICIALE')

            return HttpResponse(msg)
        except Exception as e:
            return HttpResponse(f'error inserting bet: {e}')

    
class GetPlayerInfoView(View):

    def post(self, request):
        id = request.POST.get("id")

        my_market = U.get_my_market(userid=request.user.id)

        pl = player.Player.objects.\
            filter(bet__Market_id=my_market).\
            values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date',
               'bet__Team_id__Name','bet__id','bet__Session_id','Status').\
            get(pk=id)

        pl_obj = json.dumps({'Sur':pl['Surname'], 
                             'Nam':pl['Name'], 
                             'Rol':pl['Role'],
                             'RealT':pl['RealTeam__Name'], 
                             'BetA':pl['bet__Amount'],
                             'BetE': datetime.datetime.strptime(pl['bet__Expiration_Date'], '%Y-%m-%d %H:%M:%S%z').\
                                replace(tzinfo=datetime.timezone.utc).__str__() if pl['bet__Expiration_Date'] != None else pl['bet__Expiration_Date'], #remove final timestamp
                             'BetT': pl['bet__Team_id__Name'],
                             'IsActive': pl['Status'] == 'A',
                             'BetId': pl['bet__id'],
                             'BetSessionId': pl['bet__Session_id'],
                             })

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

class FreePlayerView(View):
    def post(self, request):
        try:
            bet_id = request.POST.get("bet_id")
            session_svincolo = request.POST.get("session_svincolo")
            if (bet_id is None): return
            
            msg = U.free_player(bet_id, session_svincolo)
            
            return HttpResponse(msg)
        except Exception as e:
            return HttpResponse(f'error freeing player: {e}')