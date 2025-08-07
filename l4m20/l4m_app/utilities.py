from .models import *
from django.db.models import Q, Sum
import json
import datetime
from django.shortcuts import get_object_or_404
from django.utils import timezone
from l4m20 import constants as C

def get_my_series(teamid):
    return series.Series.objects.filter(team__id=teamid)

def get_my_markets(seriesid):
    return market.Market.objects.filter(Series_id=seriesid)

def get_players(filter_role, teamid):
    my_series = get_my_series(teamid)
    if(len(my_series) <= 0): 
        return
    my_markets = get_my_markets(my_series[0].id)
    if(len(my_markets) <= 0): 
        return

    my_market = my_markets[0].id
    
#~
    return player.Player.objects.\
        filter(Role=filter_role).\
        filter(RealTeam__isnull=False).\
        filter(mark_players__Market_id=my_market).\
        filter(Q(bet__Market_id=my_market) | Q(bet__isnull=True) | (Q(bet__isnull=False) & ~Q(bet__Market_id=my_market))).\
        exclude(Q(bet__Market_id=my_market) & Q(bet__IsExpired=True)).\
        exclude(bet__Team_id=teamid).\
        values('id','Surname','Name','Role','RealTeam__Name','mark_players__bet__Amount',
               'mark_players__bet__Expiration_Date','mark_players__bet__Team_id__Name',
               'mark_players__bet__IsExpired', 'mark_players__bet__Market_id').order_by('Surname')

def get_balance_for_bets(teamid, balance_max):
    sum = bet.Bet.objects.filter(Q(Team_id=teamid) & Q(IsExpired=False)).aggregate(Sum('Amount'))
    return (balance_max - sum['Amount__sum'] if sum['Amount__sum'] is not None else balance_max)

def get_my_best_bets(teamid, marketid):
    return bet.Bet.objects.\
        filter(Q(Team_id=teamid) & Q(Market_id=marketid)).\
        values('Amount','Player_id','Player_id__Surname','Expiration_Date','Slot',
               'IsRaised','IsExpired','id','Team_id','IsOfficial')

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
        values('id','Surname','Name','Role','bet__Team_id','bet__Amount',\
               'bet__IsExpired','bet__Carognata','bet__Expiration_Date')


def get_series_players(series_id):
	print(series_id)
   #my_series = get_my_series(teamid)
   #if(len(my_series) <= 0): 
   #    return
   #my_markets = get_my_markets(my_series[0].id)
   #if(len(my_markets) <= 0): 
   #    return
   #
   #my_market = my_markets[0].id
   #
#~ #
   #return player.Player.objects.\
   #    filter(Role=filter_role).\
   #    filter(RealTeam__isnull=False).\
   #    filter(mark_players__Market_id=my_market).\
   #    filter(Q(bet__Market_id=my_market) | Q(bet__isnull=True) | (Q(bet__isnull=False) & ~Q(bet__Market_id=my_market))).\
   #    exclude(Q(bet__Market_id=my_market) & Q(bet__IsExpired=True)).\
   #    exclude(bet__Team_id=teamid).\
   #    values('id','Surname','Name','Role','RealTeam__Name','mark_players__bet__Amount',
   #           'mark_players__bet__Expiration_Date','mark_players__bet__Team_id__Name',
   #           'mark_players__bet__IsExpired', 'mark_players__bet__Market_id').order_by('Surname')

                
def send_bet(data):
    bet_obj =  bet.Bet_Obj()
    bet_obj.Amount = int(data['betamount'])
    bet_obj.Player = data['playerid']
    bet_obj.Expiration_Date = data['exp_date']
    bet_obj.Team = data['userteamid']
    bet_obj.Slot = data['slot']
    bet_obj.Market = data['market']
    
    balance_max = data['balancemax']
    exp_date_obj = datetime.datetime.strptime(bet_obj.Expiration_Date, '%d/%m/%Y, %H:%M:%S').replace(tzinfo=timezone.get_current_timezone())

    player_ = get_object_or_404(player.Player, id=bet_obj.Player)
    user_team = get_object_or_404(team.Team, id=bet_obj.Team) #TODO: how to avoid this double fetch?
    market_ = get_object_or_404(market.Market, id=int(bet_obj.Market))
    mark_player_ = mark_players.Mark_Players.objects.filter(Q(Player_id=player_.id) & Q(Market_id=market_))

    balance_for_bets = get_balance_for_bets(bet_obj.Team, int(balance_max))
    if(bet_obj.Amount > balance_for_bets):
        return C.SendBetResult.BET_OVERFLOW, balance_max

    try:
        bet_old = bet.Bet.objects.filter(Q(Player=player_) & Q(Market=market_))
        if len(list(bet_old)) == 1: #there is an old best bet
            _bet_old = bet_old[0]
            bet_history_new = bet_history.Bet_History(
                Amount=_bet_old.Amount,
                Player=_bet_old.Player,
                Team=_bet_old.Team,
                Market=market_
            )
            bet_history_new.save()

            bet_old.delete() #remove old bet

        bet_new = bet.Bet(Amount=bet_obj.Amount,
                        Player = player_,
                        Team = user_team,
                        Expiration_Date=exp_date_obj,
                        Slot=bet_obj.Slot,
                        Market=market_,
                        Mark_player=mark_player_[0])

        bet_new.save()
    
    except Exception as e:
        # if(bet_new is not None):
        #     bet_new.delete() #rollback
        #RESCUE OLD BET FROM BET_HISTORY TODO
        raise Exception(e) 

    return (balance_for_bets - bet_obj.Amount), balance_max
    
def finalize_bet(data):

    fin_obj = squads.Squads_Obj()
    fin_obj.Amount = data['amount']
    fin_obj.Player = data['playerid']
    fin_obj.Team = data['userteamid']

    player_ = get_object_or_404(player.Player, id=fin_obj.Player)
    user_team = get_object_or_404(team.Team, id=fin_obj.Team)
    my_market_id = get_my_markets(get_my_series(user_team.id)[0].id)[0].id
    my_market = get_object_or_404(market.Market, id=my_market_id)
    last_bet = bet.Bet.objects.filter(Q(Player=player_) & Q(Market=my_market))
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
        values('id','Player__Surname','Player__RealTeam__Name','Amount','Player__Role')


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
