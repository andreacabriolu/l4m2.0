from datetime import timedelta

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Q

from ..single_models import vote, online_presence
from django.utils import timezone
from .. import statistics_utilities as SU
from .. import utilities as U


class StatisticsView(LoginRequiredMixin, View):
    template_name = 'l4m/player_statistics.html'

    def get(self, request, player_id=None):
        player_stats_aggregate = SU.aggregate_player_statistics(player_id) 
        player_stats_per_day = SU.get_player_statistics_per_day(player_id)
        
        params = {
            'player_stats': player_stats_aggregate,
            'stats_per_day': player_stats_per_day,
        }   

        return render(request, self.template_name, params)

class GetBasicStatisticsView(View):
    def get(self, request):
        player_id = request.GET['player_id']
        basic_stats = SU.aggregate_player_statistics(player_id)
        n_matches_played = vote.Vote.objects.filter(Q(Player_id=player_id) & Q(Day__gt=0)).count()
        basic_stats['n_matches_played'] = n_matches_played

        return HttpResponse(json.dumps(basic_stats))
    
class ShowcaseView(View):
    template_name = 'l4m/showcase.html'

    def get(self, request):
        user_team = U.get_user_team(request.user.id)
        teamid = user_team['id']
        logo_path = user_team['LogoPath']
        showcase_items = SU.get_showcase_items(teamid)
        
        params = {
            'showcase_data': showcase_items,
            'logo_path': logo_path,
        }   

        return render(request, self.template_name, params)  

class HallOfFameView(View):
    template_name = 'l4m/hall_of_fame.html'

    def get(self, request):
        hall_of_fame_data = SU.get_hall_of_fame_data()
        
        params = {
            'hall_of_fame_data': hall_of_fame_data,
        }   

        return render(request, self.template_name, params)

ONLINE_TIMEOUT = timedelta(seconds=60) #check if user is online in the last 60 seconds
@login_required
def heartbeat(request):

    presence, created = online_presence.OnlinePresence.objects.get_or_create(
    user=request.user
    )

    if (
        created or
        presence.last_seen < timezone.now() - ONLINE_TIMEOUT):
            presence.last_seen = timezone.now()
            presence.save(update_fields=["last_seen"])

    online_users = (
        online_presence.OnlinePresence.objects
        .filter(last_seen__gte=timezone.now() - ONLINE_TIMEOUT)
        .select_related("user")
        .order_by("user__username")
    )

    return JsonResponse({
        "count": online_users.count(),
        "users": [
            user.user.username
            for user in online_users
        ],
        "teams": [
            U.get_team_by_userid(user.user.id)['Name']
            for user in online_users
        ],
    })