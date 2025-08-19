from .models import *
from django.db.models import Q, Sum, Count, Case, When, Value, F, OuterRef, Subquery
import json
import datetime
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from zoneinfo import ZoneInfo
from l4m20 import constants as C
import statistics

def get_my_series(teamid):
    return series.Series.objects.filter(team__id=teamid)

def get_my_markets(seriesid):
    return market.Market.objects.filter(Series_id=seriesid)

def get_current_session(marketid):
    nowtime = datetime.datetime.now(ZoneInfo('Europe/Rome'))

    session_ = session.Session.objects.filter(Q(Market_id=marketid) &
                                          Q(Begin__lte=nowtime) &
                                          Q(End__gte=nowtime))
    
    if(len(session_) <=0): 
        return None
    
    return session_[0]

def get_my_market(teamid=None, userid=None):
    if teamid is None and userid is None:
        return
    if(userid is not None):
        teamid = get_user_team(userid)['id']

    myseries = get_my_series(teamid)
    if(len(myseries) <= 0): 
        return
    mymarkets = get_my_markets(myseries[0].id)
    if(len(mymarkets) <= 0): 
        return
    return mymarkets[0]

def get_players_my_series(filter_role, teamid, filtered_teams_ids):
              #~
    bet_qs =  bet.Bet.objects.filter(
        Player_id=OuterRef('pk'),
        Team_id__in=filtered_teams_ids
    ).order_by('id')
    
    return player.Player.objects.filter(
        Role=filter_role,
        RealTeam__isnull=False,
        Status='A',
    ).exclude(
        bet__Team_id=teamid
    ).annotate(
      bet__Amount=Coalesce(Subquery(bet_qs.values('Amount')[:1]), Value(None)),
      bet__Team_id__Name=Coalesce(Subquery(bet_qs.values('Team_id__Name')[:1]), Value(None)),
      bet__IsExpired=Coalesce(Subquery(bet_qs.values('IsExpired')[:1]), Value(None)),
      bet__Carognata=Coalesce(Subquery(bet_qs.values('Carognata')[:1]), Value(None)),
      bet__Expiration_Date=Coalesce(Subquery(bet_qs.values('Expiration_Date')[:1]), Value(None)),
    ).exclude(
        Q(bet__IsExpired=True) &
        Q(bet__Team_id__in=filtered_teams_ids)    
    ).values(
        'id', 'Surname', 'Name', 'Role', 'RealTeam__Name',
        'bet__Amount','bet__Team_id__Name', 'bet__IsExpired','bet__Carognata','bet__Expiration_Date'
    ).order_by('Surname')

        
def check_max_n_bets(teamid, role):
    qplayer = squads.Squads.objects.\
      filter(Q(Team_id=teamid) & Q(Quarantine=True)).first()
    
    if(qplayer):
        idq = qplayer.Player_id   
    else:
        idq = -1

    num_bets = bet.Bet.objects.\
        filter(Q(Team_id=teamid) & Q(Market_id=get_my_market(teamid).id) & Q(Player__Role=role)).\
        exclude(Q(Player_id = idq)).\
        aggregate(Count('id'))
        
    print(num_bets)    
    print(idq)    
    max_num = \
            C.NUM_GK if role == "P" else \
            C.NUM_DEF if role == "D" else \
            C.NUM_CC if role == "C" else \
            C.NUM_FW if role == "A" else -1
    
    return (
        True if num_bets['id__count'] < max_num else False
    )


def get_current_bets_amount(teamid):
    sum = bet.Bet.objects.filter(Q(Team_id=teamid) & Q(Market_id=get_my_market(teamid).id)).aggregate(Sum('Amount'))['Amount__sum']
    return sum if sum is not None else 0

def get_balance_for_bets(teamid, balance_max):
    sum = bet.Bet.objects.filter(Q(Team_id=teamid) & Q(Market_id=get_my_market(teamid).id)).aggregate(Sum('Amount'))
    #missing slot count
    num_active_bets = bet.Bet.objects.filter(Q(Team_id=teamid)).aggregate(Count('id'))
    num_missing_slots = (C.NUM_SLOTS - num_active_bets['id__count']) - 1

    return ((balance_max - sum['Amount__sum'] - num_missing_slots) if sum['Amount__sum'] is not None else balance_max - num_missing_slots)

def get_my_best_bets(teamid, marketid):
	
    qplayer = squads.Squads.objects.\
      filter(Q(Team_id=teamid) & Q(Quarantine=True)).first()
	
    bets = bet.Bet.objects.\
        filter(Q(Team_id=teamid) & Q(Market_id=marketid)).\
        values('Amount','Player_id','Player_id__Surname','Expiration_Date','Slot',
               'IsRaised','IsExpired','id','Team_id','IsOfficial','Carognata')
               
    if(qplayer is not None):
       bets = bets.exclude(Q(Player_id=qplayer.Player_id))
       
    return bets   
       
       
def list_my_best_bets(mbb):
    ls = list(mbb).__str__()
    lsr = ls.replace('\'','"')
    lsr = lsr.replace('True', 'true')
    lsr = lsr.replace('False','false')
    return lsr

def get_balance_obj(teamid):
    return balance.Balance.objects.\
        filter(Team_id=teamid)

def get_balance(teamid):
    return balance.Balance.objects.\
        filter(Team_id=teamid).\
        values('Purchases_amount','Purchases_max','N_carognate')

def get_all_team_players():
    return player.Player.objects.\
        values('id','Surname','Name','Role','bet__Team_id','bet__Amount',\
               'bet__IsExpired','bet__Carognata','bet__Expiration_Date')

                
def send_bet(data):
    bet_obj =  bet.Bet_Obj()
    bet_obj.Amount = int(data['betamount'])
    bet_obj.Player = data['playerid']
    bet_obj.Expiration_Date = data['exp_date']
    bet_obj.Team = data['userteamid']
    bet_obj.Slot = data['slot']
    bet_obj.Market = data['market']
    
    carognata = data['carognata']
    balance_max = data['balancemax']
    exp_date_obj = datetime.datetime.strptime(bet_obj.Expiration_Date, '%d/%m/%Y, %H:%M:%S').\
        replace(tzinfo=datetime.timezone.utc)   

    player_ = get_object_or_404(player.Player, id=bet_obj.Player)
    user_team = get_object_or_404(team.Team, id=bet_obj.Team) #TODO: how to avoid this double fetch?
    market_ = get_object_or_404(market.Market, id=int(bet_obj.Market))

    my_bal = get_balance_obj(bet_obj.Team)[0]
    ncarognate = my_bal.N_carognate
    balance_for_bets = get_balance_for_bets(bet_obj.Team, int(balance_max))

    if(not check_max_n_bets(user_team.id, player_.Role)):
        return C.SendBetResult.BET_SLOT_EXCEED, balance_max, ncarognate

    if(bet_obj.Amount > balance_for_bets):
        return C.SendBetResult.BET_OVERFLOW, balance_max, ncarognate

    try:
        bet_old = bet.Bet.objects.filter(Q(Player=player_) & Q(Market=market_))
        if len(list(bet_old)) == 1: #there is an old best bet
            _bet_old = bet_old[0]

            if(_bet_old.IsExpired == True):
                return C.SendBetResult.BET_EXPIRED, balance_max, ncarognate

            if(bet_obj.Amount <= _bet_old.Amount):
                return C.SendBetResult.BET_UNDERFLOW, balance_max, ncarognate

            bet_history_new = bet_history.Bet_History(
                Amount=_bet_old.Amount,
                Player=_bet_old.Player,
                Team=_bet_old.Team,
                Market=market_,
                Carognata = True if carognata=="True" else False
            )
            bet_history_new.save()

            bet_old.delete() #remove old bet

        bet_new = bet.Bet(Amount=bet_obj.Amount,
                        Player = player_,
                        Team = user_team,
                        Expiration_Date=exp_date_obj,
                        Slot=bet_obj.Slot,
                        Market=market_)

        bet_new.save()

        if(carognata == "True"):
            
            my_bal.N_carognate = ncarognate + 1

            if(my_bal.N_carognate > C.MAX_CAROGNATE): #penalty
                my_bal.Purchases_max = my_bal.Purchases_max - 1

            my_bal.save()
    
    except Exception as e:
        # if(bet_new is not None):
        #     bet_new.delete() #rollback
        #RESCUE OLD BET FROM BET_HISTORY TODO
        raise Exception(e) 

    return (my_bal.Purchases_max - get_current_bets_amount(bet_obj.Team)), balance_max, (ncarognate + 1) if (carognata == "True") else ncarognate
    
def finalize_bet(data):

    fin_obj = squads.Squads_Obj()
    fin_obj.Amount = data['amount']
    fin_obj.Player = data['playerid']
    fin_obj.Team = data['userteamid']

    player_ = get_object_or_404(player.Player, id=fin_obj.Player)
    user_team = get_object_or_404(team.Team, id=fin_obj.Team)
    my_market_id = get_my_market(fin_obj.Team).id
    my_market = get_object_or_404(market.Market, id=my_market_id)
    last_bet = bet.Bet.objects.filter(Q(Player=player_) & Q(Market=my_market))

    if(len(last_bet) < 0):
        return
    
    if(last_bet[0].IsOfficial == True):
        return C.ErrorCodes.ALREADY_OFFICIAL
    
    last_bet.update(IsOfficial=True)

    fin_new = squads.Squads(Amount=fin_obj.Amount,
                Player = player_,
                Team = user_team,
                Last_bet = last_bet[0])
    fin_new.save()            

    
def get_user_team(userid):
    return team.Team.objects.filter(Users__id=userid).values('id','Name')[0]

def get_my_players_filtered(filter_role, teamid):

    return squads.Squads.objects.\
        filter(Team_id=teamid).\
        filter(Player__Role=filter_role).\
        values('id','Player__id','Player__Surname','Player__RealTeam__Name','Amount','Player__Role').\
        order_by('Player__Surname')

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
        Series = lineup_info['series'],
        HideLineup = lineup_info['hideLineup'],
        ModNoGk = lineup_info['modNoGk'],
        )

    lineup_new.save()

def cleanJSON(jsonData):
    jsonData = jsonData.replace("'","\"") #retransform after HTML form
    jsonData = jsonData.replace("\"{","{").replace("}\"","}") #remove extra " with {
    jsonData = jsonData.replace("\\","") #remove extra \

    return jsonData    