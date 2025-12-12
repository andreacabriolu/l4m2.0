from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from .. import statistics_utilities as SU

class StatisticsView(LoginRequiredMixin, View):
    template_name = 'l4m/player_statistics.html'

    def get(self, request, player_id=None):
        player_stats = SU.aggregate_player_statistics(player_id) 
        

        params = {
            'player_stats': player_stats,
        }
        

        return render(request, self.template_name, params)

