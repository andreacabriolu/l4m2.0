from .models import *
from django.db.models import Q
import json
import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone

def get_players(filter_role, teamid):
    return player.Player.objects.\
        filter(Q(bet__Best=True) | Q(bet__Best=None)).\
        filter(Role=filter_role).\
        filter(RealTeam__isnull=False).\
        exclude(bet__Team_id=teamid).\
        values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date','bet__Team_id__Name')

def get_my_best_bets(teamid):
    return bet.Bet.objects.\
        filter((Q(Best=True) & Q(Team_id=teamid)) | (Q(IsRaised=True) & Q(Team_id=teamid))).\
        values('Amount','Player_id','Player_id__Surname','Expiration_Date','Slot','IsRaised')

def list_my_best_bets(mbb):
    ls = list(mbb).__str__()
    lsr = ls.replace('\'','"')
    lsr = lsr.replace('True', 'true')
    lsr = lsr.replace('False','false')
    return lsr

def get_balance(teamid):
    return balance.Balance.objects.\
        filter(Team_id=teamid).\
        values('Purchases_amount')

def get_total(mbb):
    #TODO implement
    pass

def get_all_team_players():
    return player.Player.objects.\
        filter(Q(bet__Best=True)).\
        values('id','Surname','Name','Role','Team_id','bet__Team_id','bet__Amount','bet__IsExpired','bet__Carognata','bet__Expiration_Date')
    
def send_bet(data):
    bet_obj =  bet.Bet_Obj()
    bet_obj.Amount = int(data['betamount'])
    bet_obj.Player = data['playerid']
    bet_obj.Expiration_Date = data['exp_date']
    bet_obj.Team = data['userteamid']
    bet_obj.Slot = data['slot']
    exp_date_obj = datetime.datetime.strptime(bet_obj.Expiration_Date, '%d/%m/%Y, %H:%M:%S').replace(tzinfo=timezone.get_current_timezone())

    player_ = get_object_or_404(player.Player, id=bet_obj.Player)
    user_team = get_object_or_404(team.Team, id=bet_obj.Team) #TODO: how to avoid this double fetch?
    bet_new = bet.Bet(Amount=bet_obj.Amount,
                    Player = player_,
                    Team = user_team,
                    Best=True,
                    Expiration_Date=exp_date_obj,
                    Slot=bet_obj.Slot)

    bet_old = bet.Bet.objects.filter(Q(Best=True) & Q(Player=player_))
    if len(list(bet_old)) == 1: #there is an old best bet
        bet_old[0].Best = False
        bet_old[0].IsRaised = True
        bet_old[0].save()

    bet_new.save()

    bal = balance.Balance.objects.filter(Team=bet_obj.Team)
    bal = bal[0] #there should be only one balance TODO: check with giamba
    bal.Purchases_amount = bal.Purchases_amount - bet_new.Amount
    bal.save()

    return bal

def get_user_team(userid):
    return team.Team.objects.filter(Users__id=userid).values('id','Name')[0]
    