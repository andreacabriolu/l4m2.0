from .models import *
from django.db.models import Q, Avg

def aggregate_player_statistics(player_id):
    _player = player.Player.objects.get(pk=player_id)
    stats = vote.Vote.objects.filter(Q(Player_id=player_id) & Q(Day__gt=0))

    if len(stats) <= 0:
        return None
    
    aggregated_stats = {
        'name_surname': f"{_player.Name} {_player.Surname}" if _player.Name is not None else f"{_player.Surname}",
        'average_vote': stats.aggregate(Avg('Vote'))['Vote__avg'].__round__(2),
        
    }

    return aggregated_stats