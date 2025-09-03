from .models import team
from . import utilities as U


def team_context(request):
    team = U.get_user_team(request.user.id)
    if len(team) <= 0:
        return
    teamname = team['Name']

    return {'teamname': teamname}
