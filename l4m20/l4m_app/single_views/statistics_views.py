from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
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

