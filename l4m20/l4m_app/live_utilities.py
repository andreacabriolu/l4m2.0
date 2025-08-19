from .models import *
import json
from l4m20 import constants as C
import statistics
from . import utilities as U
from django.db.models import Q

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

def calculate_new_module(current_module, role_tit, role_ris):
    role_combo = (role_tit, role_ris)
    return C.Modules.matrix[current_module][role_combo]

def search_substitute(votes_ris, vote_tit, module):
    good_statuses = [C.PlayerStatus.YET_TO_PLAY, C.PlayerStatus.PLAYING, C.PlayerStatus.PLAYED]
    same_role = [v for v in votes_ris if v.Player.Role == vote_tit.Player.Role 
                 and v.Status in good_statuses
                 and v.ChangedIn != ""]
    
    if len(same_role) > 0: #found
        same_role[0].ChangedIn = vote_tit.Player.Surname
        vote_tit.ChangedOut = same_role[0].Player.Surname
        return same_role[0], module
    else: #try other role, first player yet to play or with vote   
        for vote_ris in votes_ris:
            if(vote_ris.Status in good_statuses and 
               vote_ris.Player.Role != 'P' and
               check_role_with_module(vote_ris.Player.Role, module)
               ):
                vote_ris.ChangedIn = vote_tit.Player.Surname
                vote_tit.ChangedOut = vote_ris.Player.Surname
                module = calculate_new_module(module, vote_tit.Player.Role, vote_ris.Player.Role)
                return vote_ris, module

    null_vote = make_null_vote_obj(vote_tit.Player.id)
    return null_vote, module

def check_valid_module_change_for_modifier(orig, current):
    if(orig == current): return True
    
    if(orig in [C.Modules._433, C.Modules._442, C.Modules._451] and 
       current in [C.Modules._433, C.Modules._442, C.Modules._451]):
        return True
    
    if(orig in [C.Modules._532, C.Modules._541] and 
       current in [C.Modules._532, C.Modules._541]):
        return True
    
    if(orig in [C.Modules._343, C.Modules._352]):
        return False

    #TODO: manage modifier change from 5 to 4

def get_votes(lineup, current_day, my_teamid, home=True):
    votes_tit = []
    votes_ris = []
    module = C.Modules._442
    _items = []

    if(type(lineup) is str): #NO SHOW
        _items.append("noshow")
        _items.append(lineup)
        return [votes_tit, _items, votes_ris] 

    _items.append(home)
    _items.append(lineup.Team.Name)

    line = json.loads(U.cleanJSON(lineup.Line))

    if(lineup.HideLineup and lineup.Team.id != my_teamid): #HIDDEN LINEUP
        _items.append(home)
        _items.append(lineup)
        return [votes_tit, _items, votes_ris]

    cap_id = line['captain'] if 'captain' in line.keys() else 0
    orig_module = line['mod'].replace('-','')
    cap_vote = 0
    for l in line.items(): #loop players in lineup
        if l[0] == 'captain':
            continue
        if(l[0] == 'mod'):  
            module = l[1].replace('-','')
            continue
        
        pl = player.Player.objects.get(pk=l[1])
        already_played = check_already_played(pl.RealTeam)

        _vote = vote.Vote.objects.filter(Q(Player_id=l[1]) & Q(Day=current_day))
        if(l[0].endswith('tit')):
            votes_tit.append(make_vote_obj(_vote[0], cap_id, already_played) if len(_vote) > 0 else \
                             make_empty_vote_obj(l[1], cap_id, already_played))
        else:
            votes_ris.append(make_vote_obj(_vote[0], cap_id, already_played) if len(_vote) > 0 else \
                             make_empty_vote_obj(l[1], cap_id, already_played))

        if len(_vote) > 0:
            if(l[1] == cap_id):
                cap_vote = _vote[0].Vote

    #manage module change HERE
    # votes_tot = votes_tit + votes_ris
    # is_completed = C.PlayerStatus.YET_TO_PLAY not in [v.Status for v in votes_tot] and \
    #                C.PlayerStatus.PLAYING not in [v.Status for v in votes_tot]
    
    valid_votes = []
    ## get the 11 valid votes ###################
    for vote_tit in votes_tit:
        if(vote_tit.Status == C.PlayerStatus.NOT_PLAYED):
            sub, module = search_substitute(votes_ris, vote_tit, module)
            if(sub.Status == C.PlayerStatus.NO_PLAY_AT_ALL): 
                vote_tit.Status = C.PlayerStatus.NO_PLAY_AT_ALL
            vote_tit.Vote = None
            vote_tit.TotVote = None

            if(sub.Status not in [C.PlayerStatus.NO_PLAY_AT_ALL]):
                valid_votes.append(sub)
                t_i = votes_tit.index(vote_tit)
                t_r = votes_ris.index(sub)
                votes_tit[t_i], votes_ris[t_r] = votes_ris[t_r], votes_tit[t_i] #swap

        elif(vote_tit.Status in [C.PlayerStatus.PLAYED, C.PlayerStatus.PLAYING, C.PlayerStatus.YET_TO_PLAY]):
            valid_votes.append(vote_tit)

    total = sum([v.TotVote for v in valid_votes])
    _items.append(total) 

    #modificatore
    def_votes = [v.Vote for v in valid_votes if v.Player.Role=='D']
    if (len(def_votes) >= 4 and check_valid_module_change_for_modifier(orig_module, module)): 
        gk_vote = [v.Vote for v in valid_votes if v.Player.Role=='P']
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

    _noCards = len([v for v in valid_votes if v.Red or v.Yel]) == 0
    _noBadVotes = len([v for v in valid_votes if v.Vote < 6]) == 0

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
    _items.append(module)
    if(orig_module != module):
        _items.append(orig_module)

    votes_tit.sort(key=lambda vote:C.Constant_Dicts.RoleInts[vote.Player.Role])

    return [votes_tit, _items, votes_ris]
    
