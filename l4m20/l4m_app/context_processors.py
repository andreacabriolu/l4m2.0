from .models import team
from . import utilities as U


def team_context(request):
    team = U.get_user_team(request.user.id)
    if len(team) <= 0:
        return
    teamname = team['Name']

    return {'teamname': teamname}

def user_enabled_context(request):
    uid = request.user.id
    is_user_enabled = \
        uid == 1 or \
        uid == 22 or \
        uid == 23
        # uid == 24
    
    return {'is_user_enabled': is_user_enabled}

