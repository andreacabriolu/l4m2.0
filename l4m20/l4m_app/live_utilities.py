from .models import *
import json
from l4m20 import constants as C
import statistics
from . import utilities as U

def get_couples_from_calendar(seriesid, day):
    #TODO: filter per series?
    matches_ = matches_calendar.MatchesCalendar.objects.filter(CompetitionCalendar__Day=day)
    couples = [(match.HomeTeam.id, match.AwayTeam.id) for match in matches_]
    return couples

def make_null_vote_obj(pl_id, cap_id=None):
    v_obj = vote.Vote.Vote_Obj()
    pl = player.Player.objects.get(pk=pl_id)
    v_obj.Player = pl if pl is not None else None
    if(pl_id == cap_id):
        v_obj.Cap = True
    v_obj.Vote = 0
    v_obj.TotVote = 0
    v_obj.Status = C.PlayerStatus.NO_PLAY_AT_ALL
    
    return v_obj

def make_empty_vote_obj(pl_id, cap_id, already_played):
    v_obj = vote.Vote.Vote_Obj()
    pl = player.Player.objects.get(pk=pl_id)
    v_obj.Player = pl if pl is not None else None
    if(pl_id == cap_id):
        v_obj.Cap = True
    v_obj.Vote = 6
    v_obj.TotVote = 6
    v_obj.Status = C.PlayerStatus.YET_TO_PLAY if not already_played else C.PlayerStatus.NOT_PLAYED
    
    return v_obj

def make_vote_obj(_vote:vote.Vote, cap_id, already_played):
    v_obj = vote.Vote.Vote_Obj()
    v_obj.AssH = _vote.AssH
    v_obj.AssL = _vote.AssL
    v_obj.AssP = _vote.AssP
    v_obj.AssS = _vote.AssS
    v_obj.Player = _vote.Player
    v_obj.Competition = _vote.Competition
    v_obj.Day = _vote.Day
    v_obj.GoalDe = _vote.GoalDe
    v_obj.GoalSc = _vote.GoalSc
    v_obj.GoalTa = _vote.GoalTa
    v_obj.Own = _vote.Own
    v_obj.PenMi = _vote.PenMi
    v_obj.PenSa = _vote.PenSa
    v_obj.PenSc = _vote.PenSc
    v_obj.Red = _vote.Red
    v_obj.Sub = _vote.Sub 
    v_obj.Status = C.PlayerStatus.PLAYED #TODO
    v_obj.SubJ = _vote.SubJ
    v_obj.Yel = _vote.Yel
    v_obj.Vote = _vote.Vote
    v_obj.TotVote = calculate_total(_vote)
    if(_vote.Player_id == cap_id):
        v_obj.Cap = True
    v_obj.Status = C.PlayerStatus.PLAYING if not already_played else C.PlayerStatus.PLAYED

    return v_obj

def calculate_total(v):
    sum = v.Vote

    sum += \
    (v.AssH * C.Scores.ASS_HIGH) + \
    (v.AssL * C.Scores.ASS_LOW) + \
    (v.AssP * C.Scores.PENALTY_PROCURED) + \
    (v.AssS * C.Scores.ASS_STD) + \
    (v.GoalDe * C.Scores.GOAL_DECIDER) + \
    (v.GoalTa * C.Scores.GOAL_TAKEN) + \
    (v.GoalSc * C.Scores.GOAL) + \
    (v.Own * C.Scores.OWN_GOAL) + \
    (v.PenMi * C.Scores.PENALTY_MISSED) + \
    (v.PenSa * C.Scores.PENALTY_SAVED) + \
    (v.PenSc * C.Scores.PENALTY_SCORED) + \
    (v.Red * C.Scores.RED) + \
    (v.Yel * C.Scores.YELLOW)         

    return sum

def calculate_modifier(gk_vote, def_votes, modNoGk):
    if(modNoGk):
        mod = statistics.mean(def_votes)
    else:
        mod = statistics.mean(sorted(def_votes)[1:] + gk_vote)
    
    if mod < 6:
        return mod, C.Modifier_Scores._LT_6
    if 6 <= mod < 6.25:
        return mod, C.Modifier_Scores._6_625
    if 6.25 <= mod < 6.5:
        return mod, C.Modifier_Scores._625_65
    if 6.5 <= mod < 6.75:
        return mod, C.Modifier_Scores._65_675
    if 6.75 <= mod < 7:
        return mod, C.Modifier_Scores._675_7
    if 7 <= mod < 7.25:
        return mod, C.Modifier_Scores._7_725
    if 7.25 <= mod < 7.5:
        return mod, C.Modifier_Scores._725_75
    if mod >= 7.5:
        return mod, C.Modifier_Scores._GT_75
    
def calculate_n_goals(grand_total):
    diff = grand_total - C.Various.BASE_SCORE
    if (diff < 0):
        return 0
    
    return int(diff / C.Various.THRESHOLD_GOL) + 1

def check_already_played(real_team):
    #TODO check if votes in the current day contains the player real team
    return True

def check_role_with_module(role, module):
    if(role == 'D' and module in [C.Modules._532, C.Modules._541]):
        return False
    if(role == 'C' and module in [C.Modules._352, C.Modules._451]):
        return False
    if(role == 'A' and module in [C.Modules._343, C.Modules._433]):
        return False
    
    return True

def search_substitute(votes_ris, vote_tit, module):
    same_role = [v for v in votes_ris if v.Player.Role == vote_tit.Player.Role]
    
    if len(same_role) > 0: #found
        return same_role[0]
    else: #try other role, first player yet to play or with vote   
        for vote_ris in votes_ris:
            if(vote_ris.Status in [C.PlayerStatus.PLAYING, C.PlayerStatus.YET_TO_PLAY] and 
               check_role_with_module(vote_ris.Player.Role, module)
               ):
                return vote_ris

    null_vote = make_null_vote_obj(vote_tit.Player.id)
    return null_vote

def get_votes(lineup, home=True):
    votes_tit = []
    votes_ris = []
    module = C.Modules._442
    _items = []

    if(type(lineup) is str): #NO SHOW
        _items.append(home)
        _items.append(lineup)
        return [votes_tit, _items, votes_ris] 

    _items.append(home)
    _items.append(lineup.Team.Name)
    _noCards = True
    _noBadVotes = True

    line = json.loads(U.cleanJSON(lineup.Line))
    cap_id = line['captain'] if 'captain' in line.keys() else 0
    cap_vote = 0
    for l in line.items(): #loop players in lineup
        if(l[0] == 'mod'): # or l[0] == 'captain'): 
            module = l[0] 
            continue
        
        pl = player.Player.objects.get(pk=l[1])
        already_played = check_already_played(pl.RealTeam)

        _vote = vote.Vote.objects.filter(Player_id=l[1])
        if(l[0].endswith('tit')):
            votes_tit.append(make_vote_obj(_vote[0], cap_id, already_played) if len(_vote) > 0 else \
                             make_empty_vote_obj(l[1], cap_id, already_played))
        else:
            votes_ris.append(make_vote_obj(_vote[0], cap_id, already_played) if len(_vote) > 0 else \
                             make_empty_vote_obj(l[1], cap_id, already_played))

        if len(_vote) > 0:
            if(l[1] == cap_id):
                cap_vote = _vote[0].Vote
            if (_vote[0].Yel or _vote[0].Red):
                _noCards = False
            if(_vote[0].Vote < 6):
                _noBadVotes = False

    #manage module change HERE
    votes_tot = votes_tit + votes_ris
    is_completed = C.PlayerStatus.YET_TO_PLAY not in [v.Status for v in votes_tot] and \
                   C.PlayerStatus.PLAYING not in [v.Status for v in votes_tot]
    
    valid_votes = []
    ## get the 11 valid votes ###################
    for vote_tit in votes_tit:
        if(vote_tit.Status == C.PlayerStatus.NOT_PLAYED):
            sub = search_substitute(votes_ris, vote_tit, module)

    votes = votes_tit
    total = sum([v.TotVote for v in votes])
    _items.append(total) 

    #modificatore
    def_votes = [v.Vote for v in votes if v.Player.Role=='D']
    if (len(def_votes) >= 4): 
        gk_vote = [v.Vote for v in votes if v.Player.Role=='P']
        val, modifier = calculate_modifier(gk_vote, def_votes, lineup.ModNoGk)
    else:
        val, modifier = 0 , 0

    _items.append(val)
    _items.append(modifier)

    #bonus capitano
    if cap_vote > 6:
        bonus_cap = 0.5
    elif cap_vote < 6:
        bonus_cap = -0.5
    else:
        bonus_cap = 0

    #bonus disciplina
    bonus_disc = 0.5 if _noCards else 0
    #bonus prestazioni
    bonus_prest = 0.5 if _noBadVotes else 0

    _items.append(bonus_cap)
    _items.append(bonus_disc)     
    _items.append(bonus_prest)     

    grand_total = total + modifier + bonus_cap + bonus_disc + bonus_prest
    _items.append(grand_total)

    n_goals = calculate_n_goals(grand_total)
    _items.append(n_goals)

    return [votes_tit, _items, votes_ris]
    
