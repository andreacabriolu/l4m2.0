from zoneinfo import ZoneInfo

from django.shortcuts import render
from django.template.backends import django
from django.views import View
from django.http import HttpResponse, JsonResponse
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
            if (my_market is None):
                raise Exception(f'No market found for series {seriesid}')
            mbb = U.get_my_best_bets(teamid, my_market)
            current_session = U.get_current_session(my_market)
            
            filtered_teams = team.Team.objects.filter(Series__id=seriesid)
            filtered_teams_ids = [team.id for team in filtered_teams]
            my_svincoli_current_session = U.get_my_svincolati(team=teamid, session=current_session)
            players_all = U.get_all_players_my_series(teamid, filtered_teams_ids, my_svincoli_current_session, my_market)

            players_gk = [p for p in players_all if p['Role'] == 'P']
            players_def = [p for p in players_all if p['Role'] == 'D']
            players_cc = [p for p in players_all if p['Role'] == 'C']
            players_fw = [p for p in players_all if p['Role'] == 'A']

            balance = U.get_balance(teamid)[0] #TODO: improve check
            balance_for_bets = U.get_balance_for_bets(teamid, balance['Purchases_max'], my_market)
            if(balance_for_bets is None): 
                balance_for_bets = 0
            n_carognate = balance['N_carognate']
            n_svincoli = balance['N_svincoli']
            current_bets_amount = U.get_current_bets_amount(teamid, my_market)

            auction_data = {
                'summary': {
                    'active_auctions': len(mbb),
                    'user_team_id': user_team['id'],
                    'user_team_name': user_team['Name'],
                    'n_players_by_role': {
                        'P': len(players_gk),
                        'D': len(players_def),
                        'C': len(players_cc),
                        'A': len(players_fw)
                        }
                },
                'balance': {
                    'total': balance['Purchases_max'],
                    'wages': balance['Wages_amount'],
                    'wages_residual': balance['Wages_max'] - balance['Wages_amount'],
                    'wages_total': balance['Wages_max'],
                    'residual': balance['Purchases_max'] - current_bets_amount,
                    'spent': current_bets_amount,
                    'carognate': n_carognate,
                    'maxBid': balance_for_bets,
                    'n_svincoli': n_svincoli,
                },
                'players': sorted(players_all, key=lambda p: (C.Constant_Dicts.RoleInts[p['Role']], p['Surname'])),
                'bids_history': U.get_bids_history(my_market),
                'roster': list(mbb),
                'contracts_signed': U.get_signed_contracts(teamid),
                'session': {
                    'id': current_session.id,
                    'name': current_session.Name,
                    'max_nsvincoli': current_session.Nsvincoli,
                    'max_ncarognate': current_session.Ncarognate,
                    'expiration': current_session.Expiration,
                    'start': current_session.Begin.astimezone(ZoneInfo(key='Europe/Rome')).strftime('%d-%m-%Y %H:%M'),
                    'end': current_session.End.astimezone(ZoneInfo(key='Europe/Rome')).strftime('%d-%m-%Y %H:%M'),
                    'is_open': current_session.Begin <= datetime.datetime.now(ZoneInfo(key='Europe/Rome')) <= current_session.End,
                },
                'market': my_market,

            }

            params = { 
                'is_live_day': U.is_live_day(),
                'auction_data': auction_data,

            }
        except Exception as e:
            raise Exception(f'{e}')
        
        return render(request, self.template_name, params)
    
class SendBetView(View):
    template_name = 'l4m/auction.html'

    def post(self, request): 
        uname = request.user.username

        try:
            data = json.loads(request.body.decode('utf-8'))
            if (data is None): return
            
            logger.debug(f"{uname} : SENDING BET: {data}")

            bet_return = U.send_bet(data)

            if(bet_return.bet_result == C.SendBetResult.BET_SESSION_CLOSED):
                return JsonResponse({'error': 'SESSIONE DI MERCATO CHIUSA!'}, status=400)

            if(bet_return.bet_result == C.SendBetResult.BET_OVERFLOW):
                return JsonResponse({'error': 'PUNTATA TROPPO ALTA!'}, status=400)
            
            if(bet_return.bet_result == C.SendBetResult.BET_UNDERFLOW):
                return JsonResponse({'error': 'PUNTATA TROPPO BASSA!'}, status=400)

            if(bet_return.bet_result == C.SendBetResult.BET_EXPIRED):
                return JsonResponse({'error': 'GIOCATORE SCADUTO!'}, status=400)
            
            if(bet_return.bet_result == C.SendBetResult.BET_SLOT_EXCEED):
                return JsonResponse({'error': 'NUMERO MASSIMO DI GIOCATORI PER RUOLO!'}, status=400)

        except Exception as e:
            return JsonResponse({'error': f'error inserting bet and updating balance: {e}'}, status=500)
        
        return JsonResponse({'result': bet_return.bet_result,
                             'bet_id': bet_return.bet_id, 
                             'residual': bet_return.residual,
                             'total': bet_return.total, 
                             'spent': bet_return.spent,
                             'balance_for_bets': bet_return.new_balance_for_bets,
                             'n_carognate': bet_return.n_carognate,
                             'roster': list(U.get_my_best_bets(data['userteamid'], data['market']))
                            })

class FinBetView(View):
    template_name = 'l4m/auction.html'

    def post(self, request): 
        try:
            data = json.loads(request.body.decode('utf-8'))
            if (data is None): return
            
            msg = U.finalize_bet(data)
            if(msg == C.ErrorCodes.ALREADY_OFFICIAL):
                return JsonResponse({'error': 'GIOCATORE GIÀ UFFICIALE'}, status=400)

            return JsonResponse({'message': msg})
        except Exception as e:
            return JsonResponse({'error': f'error finalizing bet: {e}'}, status=500)

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
            data = json.loads(request.body.decode('utf-8'))
            if (data is None): return
            
            msg = U.free_player(data)

            if (msg == C.ErrorCodes.BET_NOT_FOUND):
                return JsonResponse({'error': 'PUNTATA NON TROVATA'}, status=400)
            elif (msg == C.ErrorCodes.BET_SESSION_CLOSED):
                return JsonResponse({'error': 'SESSIONE DI MERCATO CHIUSA!'}, status=400)
            elif (msg == C.ErrorCodes.INVALID_PARAMETERS):
                return JsonResponse({'error': 'PARAMETRI NON VALIDI'}, status=400)
            elif (msg == C.ErrorCodes.PLAYER_NOT_IN_SQUAD):
                return JsonResponse({'error': 'GIOCATORE NON NELLA SQUADRA'}, status=400)

            return JsonResponse(msg)
        except Exception as e:
            return JsonResponse({'error': f'error freeing player: {e}'}, status=500)

class SignContractView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            if (data is None): return
            
            msg = U.sign_contract(data)
            if(msg == C.ErrorCodes.PLAYER_NOT_IN_SQUAD):
                return JsonResponse({'error': 'GIOCATORE NON NELLA SQUADRA'}, status=400)
            elif(msg == C.ErrorCodes.MAX_TRIENNAL_CONTRACTS_PER_ROLE_EXCEEDED):
                return JsonResponse({'error': 'NUMERO MASSIMO DI CONTRATTI TRIENNALI PER RUOLO RAGGIUNTO'}, status=400)
            elif(msg == C.ErrorCodes.MIN_ANNUAL_CONTRACTS_PER_ROLE_NEEDED):
                return JsonResponse({'error': 'ALMENO UN CONTRATTO ANNUALE PER RUOLO NECESSARIO'}, status=400)
            elif(msg == C.ErrorCodes.BALANCE_NOT_FOUND):
                return JsonResponse({'error': 'BILANCIO NON TROVATO'}, status=400)

            return JsonResponse(msg)
        except Exception as e:
            return JsonResponse({'error': f'error signing contract: {e}'}, status=500)

class UndoBetView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            if (data is None): return

            _team = U.get_user_team(request.user.id)
            msg = U.undo_bet(data, _team)
            if(msg == C.CancelBidResult.CANCEL_NOT_FOUND):
                return JsonResponse({'error': 'PUNTATA NON TROVATA'}, status=400)
            elif(msg == C.CancelBidResult.CANCEL_EXPIRED):
                return JsonResponse({'error': 'PUNTATA SCADUTA'}, status=400)

            return JsonResponse({'message': 'PUNTATA ANNULLATA CON SUCCESSO'})
        except Exception as e:
            return JsonResponse({'error': f'error undoing bet: {e}'}, status=500)

class QuarantinePlayerView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            if (data is None): return
            
            msg = U.quarantine_player(data)
            
            if(msg == C.ErrorCodes.PLAYER_NOT_IN_SQUAD):
                return JsonResponse({'error': 'GIOCATORE NON NELLA SQUADRA'}, status=400)
            elif(msg == C.ErrorCodes.MAX_QUARANTINE_EXCEEDED):
                return JsonResponse({'error': 'NUMERO MASSIMO DI QUARANTENE RAGGIUNTO'}, status=400)

            return JsonResponse(msg)
        except Exception as e:
            return JsonResponse({'error': f'error quarantining player: {e}'}, status=500)