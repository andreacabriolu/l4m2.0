from .models import *
from django.db.models import Q, Sum, Count, Case, When, Value, F, OuterRef, Subquery
import json
import datetime
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce
from zoneinfo import ZoneInfo
from l4m20 import constants as C
import requests as req

def check_day_suspended(day):
    suspended = competition_calendar.CompetitionCalendar.objects.filter(Q(Day=day)&Q(Suspended=True)).values('Day')
    return len(suspended) > 0

def check_late_lineup(teamid, day, competition_id):
    _series = get_my_series(teamid, competition_id)
    if len(_series) > 0:
        lin = lineup.Lineup.objects.filter(Q(Day=day) & Q(Team=teamid) & Q(Series=_series[0])).values('Version').order_by('Version')

    return not (lin.first()['Version'] > (-1)) if len(lin) > 0 else False
 

def get_day_comps_lineups(day):
    teams = team.Team.objects.all().values('id','Name')
    team_lups_comps = {}

    for t in teams:
        t_nlineups = get_my_lineups_by_day_distinct(t['id'], day)
        t_comps = get_my_active_competitions_filtered(t['id'], day)
        
        team_lups_comps[t['id']] = { 'tname':t['Name'], 'nlineups': t_nlineups['nlin'], 'ncomps': len(t_comps), \
                                    'full': t_nlineups['nlin'] - len(t_comps) == 0}

    return team_lups_comps

def get_my_lineups_competitions_by_day(teamid, day):
    return lineup.Lineup.objects.filter(Q(Team=teamid) & Q(Day=day)).values('Series_id__Competition_id')

def get_my_lineups_by_day_distinct(teamid, day):
    return lineup.Lineup.objects.filter(Q(Team=teamid) & Q(Day=day)).aggregate(nlin=Count('Series_id', distinct=True))

def get_my_active_competitions_filtered(teamid, day):
    return competition.Competition.objects.filter(Q(Active=True) & \
                                                  Q(Lineup=True) & \
                                                  Q(team_competition__Team_id=teamid) & \
                                                  Q(competitioncalendar__Day=day))

def get_results_calendar(series_id, day):
    results = []
    mcs = matches_calendar.MatchesCalendar.objects.filter(Q(Series_id=series_id) ) 
    
    for mc in mcs:
        ngoals_home = matches_results.MatchesResults.objects.filter(Q(MatchesCalendar_id=mc.id) & Q(Team_id=mc.HomeTeam.id)).values('NGoals')
        ngoals_away = matches_results.MatchesResults.objects.filter(Q(MatchesCalendar_id=mc.id) & Q(Team_id=mc.AwayTeam.id)).values('NGoals')

        results.append([
            f'GIORNATA {mc.CompetitionCalendar.Day}',
            mc.HomeTeam.Name,
            ngoals_home[0]['NGoals'] if len(ngoals_home) > 0 else '-',
            ngoals_away[0]['NGoals'] if len(ngoals_away) > 0 else '-',
            mc.AwayTeam.Name,
            ])
    
    return results

def is_current_day_completed():
    url = "https://publicapi.fantamaster.it/livescores/?tcache=1756165942189"
    resp = req.get(url)
    resp_content = resp.content
    resp_json = json.loads(resp_content)
    resp_day = resp_json['day']

    for score in resp_json['scores']:
        if score['time'] != C.Events.END_MATCH:
            return False, resp_day

    return True, resp_day

def clean_name(name):
    return name.replace(' ','_').replace('\'','')

def get_last_available_ranking_by_day(c_id, s_id, day):
    r = ranking.Ranking.objects.filter(Q(Competition=c_id) & Q(Series=s_id) & Q(Day__lt=day)).order_by('-Day')
    if len(r) <= 0:
        return None

    return r

def get_last_available_ranking(c_id, s_id):
    r = ranking.Ranking.objects.filter(Q(Competition=c_id) & Q(Series=s_id)).order_by('-Day')
    if len(r) <= 0:
        return None

    return r

def get_ranking(c_id, s_id, day):
    #check the first not suspended day before (any competition, since b11 is not listed as regular competition)
    if check_day_suspended(day):
        days = competition_calendar.CompetitionCalendar.objects.filter(Q(Suspended=False)&Q(Day__lt=day)).values('Day').order_by('-Day')
        if len(days) <= 0:
            return None
        day = days[0]['Day']

    r = ranking.Ranking.objects.filter(Q(Competition=c_id) & Q(Series=s_id) & Q(Day=int(day)))
    if len(r) <= 0:
        return None

    return r

def get_days(c_id):
    return competition_calendar.CompetitionCalendar.objects.filter(Q(Competition=c_id)&Q(Suspended=False)).values('Day')

def get_competition_by_id(id):
    return competition.Competition.objects.get(pk=id)

def get_competition(name):
    return competition.Competition.objects.filter(Name=name)

def get_all_competitions():
    return competition.Competition.objects.all()

def get_all_active_competitions():
    return competition.Competition.objects.filter(Q(Active=True))

def get_all_live_competitions():
    return competition.Competition.objects.filter(Q(Live=True))

def get_all_live_active_competitions():
    return competition.Competition.objects.filter(Q(Active=True) & Q(Live=True))

def get_all_lineup_active_competitions():
    return competition.Competition.objects.filter(Q(Active=True) & Q(Lineup=True))

def get_my_lineup_active_competitions(my_series, day):
    return competition.Competition.objects.filter(Q(Active=True) & \
                                                  Q(Lineup=True) & \
                                                  Q(series__id__in=my_series) & \
                                                  Q(competitioncalendar__Day=day))
    #TODO modify:
    #competition.Competition.objects.filter(Q(Active=True) & \
    #                                              Q(Lineup=True) & \
    #                                              Q(team_competition__Team_id=t['id']) & \
    #                                              Q(competitioncalendar__Day=day))

def get_all_today_competitions(day):
    return competition.Competition.objects.filter(Q(Active=True) & \
                                                  Q(Live=True) & \
                                                  Q(competitioncalendar__Day=day))

def get_my_competitions(my_series):
    return competition.Competition.objects.filter(series__id__in=my_series)

def get_homeaway(competitionid, day):
    cc= competition_calendar.CompetitionCalendar.objects.filter(Q(Competition=competitionid)&Q(Day=day)).values('HomeAway')
    return cc.first()['HomeAway'] if len(cc)>0 else False

def get_unica_series(competitionid):
    return series.Series.objects.filter(Q(Name='Unica') & Q(Competition_id=competitionid))

def get_my_series(teamid, competitionid=1):
    return series.Series.objects.filter(Q(team=teamid) & Q(Competition=competitionid))

def get_all_my_series(teamid):
    return series.Series.objects.filter(Q(team=teamid))

def get_all_series(competitionid):
    return series.Series.objects.filter(Competition_id=competitionid)

def get_my_markets(seriesid):
    return market.Market.objects.filter(Series_id=seriesid)

def get_squads(teamid):
    return squads.Squads.objects.filter(Q(Team_id=teamid)&Q(Quarantine=False))

def get_players_by_squad(_squads):
    pl_ids = [pl.Player_id for pl in _squads]
    return player.Player.objects.filter(id__in=pl_ids).values('id','Surname','Role','RealTeam')

def get_players_by_lups(l_ups):
    _lups = []
    for l_up in l_ups:
        j = json.loads(cleanJSON(l_up.Line))
        _lups.append([v for _,v in j.items()][1:])

    pl_ids = list(set().union(*_lups))

    return player.Player.objects.filter(id__in=pl_ids).values('id','Surname','Role')

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

def get_my_svincolati(team, session=None):
    svincoli_list = \
        bet_history.Bet_History.objects.filter(Q(Team=team) & Q(Svincolo=True) & Q(Session_svincolo=session)) if session is not None else \
        bet_history.Bet_History.objects.filter(Q(Team=team) & Q(Svincolo=True))
    
    return [s.Player_id for s in svincoli_list]

def get_players_my_series(filter_role, teamid, filtered_teams_ids, my_svincoli_current_session):
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
    ).exclude(
        Q(id__in=my_svincoli_current_session)
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

def update_balance_latelineup(bal):
    n_non_schierate = bal.N_formazioni_non_schierate
    bal.N_formazioni_non_schierate = n_non_schierate + 1
    bal.save()

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
        values('Purchases_amount','Purchases_max','N_carognate','N_svincoli')

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
    bet_obj.Session = data['session']
    
    carognata = data['carognata']
    balance_max = data['balancemax']
    exp_date_obj = datetime.datetime.strptime(bet_obj.Expiration_Date, '%d/%m/%Y, %H:%M:%S').\
        replace(tzinfo=datetime.timezone.utc)   

    player_ = get_object_or_404(player.Player, id=bet_obj.Player)
    user_team = get_object_or_404(team.Team, id=bet_obj.Team) #TODO: how to avoid this double fetch?
    market_ = get_object_or_404(market.Market, id=int(bet_obj.Market))
    session_ = session.Session.objects.get(pk=bet_obj.Session)

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
                Session=session_,
                Carognata = True if carognata=="True" else False
            )
            bet_history_new.save()

            bet_old.delete() #remove old bet

        bet_new = bet.Bet(Amount=bet_obj.Amount,
                        Player = player_,
                        Team = user_team,
                        Expiration_Date=exp_date_obj,
                        Slot=bet_obj.Slot,
                        Market=market_,
                        Session=session_)

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
    return team.Team.objects.filter(Users__id=userid).values('id','Name','LogoPath')[0]

def get_my_players_filtered(filter_role, teamid):

    return squads.Squads.objects.\
        filter(Team_id=teamid).\
        filter(Player__Role=filter_role).\
        filter(Quarantine=False).\
        values('id','Player__id','Player__Surname','Player__RealTeam__Name','Amount','Player__Role', 'Player__RealTeam__id').\
        order_by('Player__Surname')

def complete_list(l, num_max, role):
    if(len(l) < num_max):
        for _ in range(num_max - len(l)):
            l.append({"id": "-1", "Role":role})
    
    return l

def get_current_day(competition_id=""):
    day = config.Config.objects.filter(Name="CurrentDay").first()
    return day.Value

def get_team_by_name(tname):
    return team.Team.objects.get(Name=tname)

def get_all_lineups(teamid, day, seriesid):
    return lineup.Lineup.objects.filter(Team=teamid, Day=day, Series=seriesid).order_by('Version')

def get_last_valid_lineup(teamid, comp_id=1):
    my_series = get_my_series(teamid, comp_id)[0]
    all_lups = lineup.Lineup.objects.filter(Team=teamid, Series=my_series.id).order_by('-Version').order_by('-Day')
    return list(all_lups)[0]

def get_last_lineup(teamid, day, comp_id=1):
    my_series = get_my_series(teamid, comp_id)[0]
    return lineup.Lineup.objects.filter(Team=teamid, Day=day, Series=my_series.id).order_by('-Version')[:1]

def save_last_valid_lineup(_lineup, day, seriesid):
    last_lineup_late = lineup.Lineup(
        Line = _lineup.Line,
        Day = day,
        Version = -1, #LATE LINEUP
        Team = _lineup.Team,
        Timestamp = datetime.datetime.now(),
        Series = series.Series.objects.get(pk=seriesid),
        HideLineup = _lineup.HideLineup,
        ModNoGk = _lineup.ModNoGk,
        LateEdit = False
    )

    last_lineup_late.save()

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
        LateEdit = lineup_info['late_edit']
        )

    lineup_new.save()

def cleanJSON(jsonData):
    jsonData = jsonData.replace("'","\"") #retransform after HTML form
    jsonData = jsonData.replace("\"{","{").replace("}\"","}") #remove extra " with {
    jsonData = jsonData.replace("\\","") #remove extra \

    return jsonData    

def check_day_already_started(day):
    today_matches = real_calendar.Real_calendar.objects.filter(Day=day).values('Date').order_by('Date')
    day_time_limit = today_matches.first()['Date'].astimezone(ZoneInfo(key='Europe/Rome')) if len(today_matches) > 0 else None
    if day_time_limit is None:
        return False, datetime.datetime.now(ZoneInfo('Europe/Rome'))
    return datetime.datetime.now(ZoneInfo('Europe/Rome')) >= day_time_limit, day_time_limit

def free_player(bet_id, session_svincolo):
    _bet = bet.Bet.objects.get(pk=int(bet_id))

    _squad = squads.Squads.objects.filter(Q(Team=_bet.Team_id) & Q(Player=_bet.Player))
    if(_squad is None):
        return
    _squad.delete()

    bet_history_new = bet_history.Bet_History(
            Amount=_bet.Amount,
            Player=_bet.Player,
            Team=_bet.Team,
            Market=_bet.Market,
            Session=_bet.Session,
            Carognata = True if _bet.Carognata==True else False,
            Svincolo = True,
            Session_svincolo = session.Session.objects.get(pk=session_svincolo)
            )
    
    bet_history_new.save()

    my_bal = get_balance_obj(_bet.Team_id)
    if len(my_bal) <= 0:
        return
    
    my_bal = my_bal[0]
    my_bal.N_svincoli = my_bal.N_svincoli + 1

    max_svincoli = _bet.Session.Nsvincoli

    if(my_bal.N_svincoli > max_svincoli): #penalty
        my_bal.Purchases_max = my_bal.Purchases_max - 1

    my_bal.save()

    _bet.delete()

def calculate_n_goals(fp_total): #replicate of live utilities method to avoid circular ref
    diff = fp_total - C.Various.BASE_SCORE
    if (diff < 0):
        return 0
    
    return int(diff / C.Various.THRESHOLD_GOL) + 1    

def get_scores(t_id):
    results_fp = matches_results.MatchesResults.objects.filter(Team=t_id).order_by('id').values('Fp')
    fps = []
    for res in list(results_fp):
        fps.append(res['Fp'])
    
    return fps

def count_non_schierate(t_id):
    non_schierate = matches_results.MatchesResults.objects.filter(Q(Pen=1)&Q(Team=t_id)).aggregate(num=Count("MatchesCalendar__CompetitionCalendar__Day"))
    return non_schierate['num']

def check_penalties(t_id, day, comp_id):
    l = get_last_lineup(t_id, day, comp_id=comp_id)[0]

    if l.Version > 0:
        return 3, 1, 0 #standard
    
    if l.Version < 0: #TODO: in case of recalculation this counter is wrong! use march_result instead
        n_non_schierate = count_non_schierate(t_id)
        if n_non_schierate <= C.MAX_NON_SCHIERATE:
            return 0, 0, 0 #0 pt
        else:
            return -1, -1, -1 #-1 pt 
