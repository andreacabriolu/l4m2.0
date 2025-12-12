from .models import *
from django.db.models import F, Q, Avg
from l4m20 import constants as C

def aggregate_player_statistics(player_id):
    _player = player.Player.objects.get(pk=player_id)
    stats = vote.Vote.objects.filter(Q(Player_id=player_id) & Q(Day__gt=0))

    if len(stats) <= 0:
        return None
    
    aggregated_stats = {
        'name_surname': f"{_player.Name} {_player.Surname}" if _player.Name is not None else f"{_player.Surname}",
        'role': C.Constant_Dicts.RoleNames[_player.Role],
        'realteam': _player.RealTeam.Name,
        'average_vote': stats.aggregate(Avg('Vote'))['Vote__avg'].__round__(2),
        'average_fantamedia': stats.aggregate(Avg('TotVote'))['TotVote__avg'].__round__(2),
        'goals': stats.aggregate(total_goals=models.Sum('GoalSc'))['total_goals'] or 0,
        'goals_conceded': stats.aggregate(total_goals_conceded=models.Sum('GoalTa'))['total_goals_conceded'] or 0,
        'penalties_scored': stats.aggregate(total_penalties_scored=models.Sum('PenSc'))['total_penalties_scored'] or 0,
        'penalties_missed': stats.aggregate(total_penalties_missed=models.Sum('PenMi'))['total_penalties_missed'] or 0,
        'penalties_saved': stats.aggregate(total_penalties_saved=models.Sum('PenSa'))['total_penalties_saved'] or 0,
        'own_goals': stats.aggregate(total_own_goals=models.Sum('Own'))['total_own_goals'] or 0,
        'assists': stats.aggregate(total_assists=models.Sum('AssS'))['total_assists'] or 0,
        'yellow_cards': stats.aggregate(total_yellow_cards=models.Sum('Yel'))['total_yellow_cards'] or 0,
        'red_cards': stats.aggregate(total_red_cards=models.Sum(F('Red') + F('YelRed')))['total_red_cards'] or 0,
        'penalty_wins': stats.aggregate(total_penalty_wins=models.Sum('AssP'))['total_penalty_wins'] or 0,


        
    }

    return aggregated_stats