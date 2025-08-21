from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from .. import utilities as U
from .. import live_utilities as LU
from ..models import *
from l4m20 import constants as C

class LiveView(LoginRequiredMixin, View):
    template_name = 'l4m/live.html'

    def enrich_and_sort_players(self, role, teamid, current_day, cap_id=-1):
        players = U.get_my_players_filtered(role, teamid)
        enriched_players = []
    
        for keep in players:
            idpl = keep["Player__id"]
            pl = player.Player.objects.get(pk=idpl)
            already_played = LU.check_already_played(current_day, pl.RealTeam)
    
            _vote = vote.Vote.objects.filter(Q(Player_id=idpl) & Q(Day=current_day))
            votes_pl = LU.make_vote_obj(_vote[0], cap_id, already_played) if len(_vote) > 0 else \
                       LU.make_empty_vote_obj(pl.id, cap_id, already_played, current_day)
    
            pl.votes = votes_pl
            enriched_players.append(pl)
    
        # sort by TotVote, then by Vote
        sorted_players = sorted(
            enriched_players,
            key=lambda p: (
                p.votes.TotVote if p.votes.TotVote is not None else -1,
                p.votes.Vote if p.votes.Vote is not None else -1
            ),
            reverse=True
        )
    
        return sorted_players


    def pick_best_11(self, keepers, defenders, midfielders, attackers):
        best_lineup = None
        best_score = -1

        ALLOWED_MODULES = [
            (3, 4, 3),
            (3, 5, 2),
            (4, 3, 3),
            (4, 4, 2),
            (4, 5, 1),
            (5, 4, 1),
            (5, 3, 2),
        ]    
       
        for d, m, a in ALLOWED_MODULES:
            try:
                lineup = []
                lineup.append(keepers[0])
                lineup += defenders[:d]
                lineup += midfielders[:m]
                lineup += attackers[:a]
    
                score = sum(
                    (p.votes.TotVote if p.votes.TotVote is not None else -1)
                    for p in lineup
                )
    
                if score > best_score:
                    best_score = score
                    best_lineup = {
                        "module": f"{d}-{m}-{a}",
                        "players": lineup,
                        "score": score
                    }
            except IndexError:
                # not enough players to fill that module → skip
                continue
    
        return best_lineup        
    
    def get(self,request):
        current_day = U.get_current_day()
        teamid = U.get_user_team(request.user.id)['id']
        seriesid = U.get_my_series(teamid)[0].id                     
        
        # Separate groups
        keep = self.enrich_and_sort_players('P', teamid, current_day)
        difs = self.enrich_and_sort_players('D', teamid, current_day)
        mids = self.enrich_and_sort_players('C', teamid, current_day)
        atts = self.enrich_and_sort_players('A', teamid, current_day)
        
        best = self.pick_best_11(keep, difs, mids, atts)
        
        print("Best module:", best["module"], "score:", best["score"])
        for p in best["players"]:
            print(p.Surname, p.votes.Vote, p.votes.TotVote)
                               
                       
        series_teams = team.Team.objects.filter(Series__id=seriesid)
        last_lineups_d = {}
        for t in series_teams:
            l = U.get_last_lineup(t, current_day)
            last_lineups_d[t.id] = l[0] if len(l) > 0 else t.Name #TODO: get last valid lineup
        
        last_lineups_d={teamid:last_lineups_d.pop(teamid), **last_lineups_d} #get user lineup as first

        couples = LU.get_couples_from_calendar(seriesid, current_day)
        lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]]) for c in couples ]

        all_votes = []

        for lineup_couple in lineup_couples:
            votes_home = LU.get_votes(lineup_couple[0], current_day, teamid)
            votes_away = LU.get_votes(lineup_couple[1], current_day, teamid, home=False)
            all_votes.append( \
                [votes_home, votes_away]
            )
            
        params = { 
            'all_votes' : all_votes,
          }
        
        return render(request, self.template_name, params)
    
