from .models import *
from django.db.models import Q


def get_query_players(filter_role):
    return player.Player.objects.\
            filter(Q(bet__Best=True) | Q(bet__Best=None)).\
            filter(Role=filter_role).\
            filter(RealTeam__isnull=False).\
                values('id','Surname','Name','Role','RealTeam__Name','bet__Amount','bet__Expiration_Date','bet__Team_id')
