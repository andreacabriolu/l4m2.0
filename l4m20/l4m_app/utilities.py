from .models import *
from django.db.models import Q
import json
import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone

def get_players(filter_role, teamid):
    return player.Player.objects.\
        filter(Role=filter_role).\
        filter(RealTeam__isnull=False).\
        exclude(bet__Team_id=teamid).\
        values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date','bet__Team_id__Name')

def get_my_best_bets(teamid):
    return bet.Bet.objects.\
        filter((Q(Team_id=teamid)) | (Q(IsRaised=True) & Q(Team_id=teamid))).\
        values('Amount','Player_id','Player_id__Surname','Expiration_Date','Slot','IsRaised','IsExpired','id','Team_id','IsOfficial')

def list_my_best_bets(mbb):
    ls = list(mbb).__str__()
    lsr = ls.replace('\'','"')
    lsr = lsr.replace('True', 'true')
    lsr = lsr.replace('False','false')
    return lsr

def get_balance(teamid):
    return balance.Balance.objects.\
        filter(Team_id=teamid).\
        values('Purchases_amount','Purchases_max')

def get_total(mbb):
    #TODO implement
    pass

def get_all_team_players():
    return player.Player.objects.\
        values('id','Surname','Name','Role','Team_id','bet__Team_id','bet__Amount',\
               'bet__IsExpired','bet__Carognata','bet__Expiration_Date')
    
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

    try:
        bet_old = bet.Bet.objects.filter(Q(Player=player_))
        if len(list(bet_old)) == 1: #there is an old best bet
            _bet_old = bet_old[0]
            bet_history_new = bet_history.Bet_History(
                Amount=_bet_old.Amount,
                Player=_bet_old.Player,
                Team=_bet_old.Team
            )
            bet_history_new.save()

            #Give back the spent money to the old betting team
            bal_oldteam = balance.Balance.objects.filter(Team=_bet_old.Team)
            bal_oldteam = bal_oldteam[0]
            bal_oldteam.Purchases_amount = bal_oldteam.Purchases_amount + _bet_old.Amount
            bal_oldteam.save()
    
    except Exception as e:
        bet_new.delete() #rollback
        bal_newteam.Purchases_amount = bal_newteam.Purchases_amount + bet_new.Amount #rollback
        raise Exception(e) 

    if len(list(bet_old)) == 1: #there is an old best bet
        try:
            bet_old.delete() #remove old bet
        except Exception as e:
            bet_new.delete() #rollback
            bal_newteam.Purchases_amount = bal_newteam.Purchases_amount + bet_new.Amount #rollback
            bal_oldteam.Purchases_amount = bal_oldteam.Purchases_amount - _bet_old.Amount
            raise Exception(e) 
        
    try:
        bet_new = bet.Bet(Amount=bet_obj.Amount,
                        Player = player_,
                        Team = user_team,
                        Expiration_Date=exp_date_obj,
                        Slot=bet_obj.Slot)

        bet_new.save()

    except Exception as e:
        raise Exception(e) 

    try:
        #Take back the spent money from the betting team
        bal_newteam = balance.Balance.objects.filter(Team=bet_obj.Team)
        bal_newteam = bal_newteam[0] #there should be only one balance TODO: check with giamba
        bal_newteam.Purchases_amount = bal_newteam.Purchases_amount - bet_new.Amount
        bal_newteam.save()

    except Exception as e:
        bet_new.delete() #rollback
        raise Exception(e)

    return bal_newteam
    
def finalize_bet(data):

    fin_obj = squads.Squads_Obj()
    fin_obj.Amount = data['amount']
    fin_obj.Player = data['playerid']
    fin_obj.Team = data['userteamid']

    player_ = get_object_or_404(player.Player, id=fin_obj.Player)
    user_team = get_object_or_404(team.Team, id=fin_obj.Team)
    last_bet = bet.Bet.objects.filter(Q(Player_id=player_.id))
    last_bet.update(IsOfficial=True)

    fin_new = squads.Squads(Amount=fin_obj.Amount,
                Player = player_,
                Team = user_team)
    fin_new.save()            
                
    # return fin_obj.userteamid

    
def get_user_team(userid):
    return team.Team.objects.filter(Users__id=userid).values('id','Name')[0]

def get_user_series():
    return get_object_or_404(series.Series, Name="serie A".lower()) #TODO: implement

def get_my_players(filter_role, teamid):

    return squads.Squads.objects.\
        filter(Team_id=teamid).\
        filter(Player__Role=filter_role).\
        values('id','Player__Surname','Player__RealTeam__Name','Jersey_num','Player__Role')


def complete_list(l, num_max, role):
    if(len(l) < num_max):
        for _ in range(num_max - len(l)):
            l.append({"id": "-1", "Role":role})
    
    return l

def get_current_day():
    #TODO: to be implemented, get the current day based on calendar
    return 1 #TEMP

def get_last_lineup(teamid, day):
    return lineup.Lineup.objects.filter(Team=teamid, Day=day).order_by('-Version')[:1]
    
def save_lineup(lineup_info):
    lineup_new = lineup.Lineup(
        Line = lineup_info['line'],
        Day = lineup_info['day'],
        Version = lineup_info['version'],
        Team = get_object_or_404(team.Team, id=lineup_info['team']),
        Timestamp = lineup_info['timestamp'],
        Series = lineup_info['series']
        )

    lineup_new.save()

def cleanJSON(jsonData):
    jsonData = jsonData.replace("'","\"") #retransform after HTML form
    jsonData = jsonData.replace("\"{","{").replace("}\"","}") #remove extra " with {
    jsonData = jsonData.replace("\\","") #remove extra \

    return jsonData    
