from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from l4m_app.single_models import vote
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