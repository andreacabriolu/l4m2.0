from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.views import View, generic
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from datetime import datetime
from django.utils import timezone
from django.db.models import Q

from . import utilities as U
from .models import *
from l4m20 import constants as C



class LoginView(View):
    template_name= 'l4m/login.html'
    
    def get(self,request):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/l4m/') #TODO: redirect based on roles!
        else:
            return render(request, self.template_name, {'form': form})
        
class AuctionView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/auction.html'
    login_url = '/login/'

    def get(self,request):
        user_team = team.Team.objects.filter(Users__id=request.user.id).values('id','Name')[0]
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

            # bet_obj =  bet.Bet_Obj()
            # bet_obj.Amount = int(data['betamount'])
            # bet_obj.Player = data['playerid']
            # bet_obj.Expiration_Date = data['exp_date']
            # bet_obj.Team = data['userteamid']
            # bet_obj.Slot = data['slot']
            # exp_date_obj = datetime.strptime(bet_obj.Expiration_Date, '%d/%m/%Y, %H:%M:%S').replace(tzinfo=timezone.get_current_timezone())

            # player_ = get_object_or_404(player.Player, id=bet_obj.Player)
            # user_team = get_object_or_404(team.Team, id=bet_obj.Team) #TODO: how to avoid this double fetch?
            # bet_new = bet.Bet(Amount=bet_obj.Amount,
            #                 Player = player_,
            #                 Team = user_team,
            #                 Best=True,
            #                 Expiration_Date=exp_date_obj,
            #                 Slot=bet_obj.Slot)

            # bet_old = bet.Bet.objects.filter(Q(Best=True) & Q(Player=player_))
            # if len(list(bet_old)) == 1: #there is an old best bet
            #     bet_old[0].Best = False
            #     bet_old[0].save()

            # bet_new.save()

            # bal = balance.Balance.objects.filter(Team=bet_obj.Team)
            # bal = bal[0] #there should be only one balance TODO: check with giamba
            # bal.Purchases_amount = bal.Purchases_amount - bet_new.Amount
            # bal.save()
        except:
            return HttpResponse('error inserting bet and updating balance')
        
        return HttpResponse(json.dumps({'new_bal' : bal.Purchases_amount}))
    
class GetPlayerInfoView(View):

    def post(self, request):
        id = request.POST.get("id")

        pl = player.Player.objects.\
        filter(Q(bet__Best=True) | Q(bet__Best=None)).\
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
        team_ids = team.Team.objects.all().values('id')
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

            team_players[team_id['id']] = lp + ld + lc + la

        params = { 
            'team_players' : json.dumps(team_players)
          }
        
        return render(request, self.template_name, params)