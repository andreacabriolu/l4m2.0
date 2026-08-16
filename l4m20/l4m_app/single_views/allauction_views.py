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

class AllAuctionsView(LoginRequiredMixin, View):
    template_name = 'l4m/allauctions.html'

    def get(self,request, series_id=None):

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
        filtered_teams = team.Team.objects.filter(Series__id=seriesid)
        market_id = U.get_my_markets(seriesid)[0].id #TODO: improve check
        
        user_team_name = U.get_user_team(request.user.id)['Name'].replace(' ','_')
        team_players = {}
        balances = {}
        
        for _team in filtered_teams:
            qplayer = squads.Squads.objects.\
             filter(
                 Q(Team_id=_team.id) & 
                 Q(Quarantine=True) &
                 Q(Season_id__Active=True)).first()
            
            if(qplayer):
                idq = qplayer.Player_id
                surq = qplayer.Player.Surname
                bet = qplayer.Last_bet
                if(bet):
                   qam = bet.Amount
            else:
                idq = -1
                surq = '-'
                qam = ''
                        
            lp = list(all_team_players.filter(Q(bet__Team_id=_team.id) & Q(bet__Market_id=market_id) \
                        & Q(Role=C.Constant_Dicts.RoleChars['POR'])).exclude(Q(id=idq)))
            ld = list(all_team_players.filter(Q(bet__Team_id=_team.id) & Q(bet__Market_id=market_id) \
                        & Q(Role=C.Constant_Dicts.RoleChars['DIF'])).exclude(Q(id=idq)))
            lc = list(all_team_players.filter(Q(bet__Team_id=_team.id) & Q(bet__Market_id=market_id) \
                        & Q(Role=C.Constant_Dicts.RoleChars['CC'])).exclude(Q(id=idq)))
            la = list(all_team_players.filter(Q(bet__Team_id=_team.id) & Q(bet__Market_id=market_id) \
                        & Q(Role=C.Constant_Dicts.RoleChars['ATT'])).exclude(Q(id=idq)))
            
            balances_ = U.get_balance(_team.id)
            if len(balances_) <= 0: 
                continue

            lp.sort(key=lambda x: x['bet__Expiration_Date'])
            ld.sort(key=lambda x: x['bet__Expiration_Date'])
            lc.sort(key=lambda x: x['bet__Expiration_Date'])
            la.sort(key=lambda x: x['bet__Expiration_Date'])

            balance = balances_[0]
            balance_for_bets = U.get_balance_for_bets(_team.id, balance['Purchases_max'])
            
            amount = balance['Purchases_max']
            pmax = balance_for_bets
            current_bets_amount = U.get_current_bets_amount(_team.id, market_id)

            li = [{'Surname': 'Monte Acquisti', 'Name': None, 'bet__Team_id': _team.id, 'bet__Amount': amount, 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Restante', 'Name': None, 'bet__Team_id': _team.id, 'bet__Amount': (amount - current_bets_amount), 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Puntata Massima', 'Name': None, 'bet__Team_id': _team.id, 'bet__Amount': pmax, 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Carognate', 'Name': None, 'bet__Team_id': _team.id, 'bet__Amount': balance['N_carognate'], 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  {'Surname': 'Q: '+str(surq), 'Name': None, 'bet__Team_id': _team.id, 'bet__Amount': qam, 'bet__IsExpired': True, 'bet__Carognata': False, 'bet__Expiration_Date': '','id':"0", 'Role': 'I'},
                  ]
            
            lp = U.complete_list(lp, C.NUM_GK, C.Constant_Dicts.RoleChars['POR'])
            ld = U.complete_list(ld, C.NUM_DEF, C.Constant_Dicts.RoleChars['DIF'])
            lc = U.complete_list(lc, C.NUM_CC, C.Constant_Dicts.RoleChars['CC'])
            la = U.complete_list(la, C.NUM_FW, C.Constant_Dicts.RoleChars['ATT'])

            team_players[_team.Name.replace(' ','_')] = lp + ld + lc + la + li

            # #TODO: manage more than 1 balance!
            # balance = U.get_balance(team_id['id'])
            # if(not balance):
            #     continue
            balances[_team.Name.replace(' ','_')] = U.get_balance_for_bets(_team.id, balance['Purchases_max'])
            
         
        filtered_team_ids = {t.id for t in filtered_teams}
        

        team_players = {
            team_name: [p for p in players if p.get('bet__Team_id') in filtered_team_ids]
            for team_name, players in team_players.items()
        }     
        
        if(seriesid == myseries):
            team_players={user_team_name:team_players.pop(user_team_name), **team_players} #get user team as first

        params = { 
            'team_players' : json.dumps(team_players),
            'balances' : json.dumps(balances)
          }
        
        return render(request, self.template_name, params)
