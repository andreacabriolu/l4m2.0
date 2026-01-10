from django.core import serializers
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.contrib.auth.decorators import login_required
from requests import request


from .. import utilities as U
from .. import live_utilities as LU
from ..models import *

class GetPenaltiesView(View):
    def get(self, request):
        t = U.get_team_by_name(request.GET['tname'])
        day = request.GET['day']
        current_day = U.get_current_day()
        competition_id = request.GET['competition']
        lineup = U.get_last_lineup(t, day, comp_id=competition_id)[0]

        opponents = LU.get_opponent_from_calendar(t.id, day, competition_id)
        if len(opponents) <= 0:
            return HttpResponse(json.dumps({}))
        opponent = opponents[0]
        opponent_lineup = U.get_last_lineup(opponent, day, comp_id=competition_id)[0]

        #QUICK LOAD THE PAST
        if int(day) < int(current_day):
            _match = LU.get_match_from_calendar(t.id, day, competition_id)
            if len(_match) <= 0:
                return HttpResponse(json.dumps({}))
            
            mr = LU.get_match_result(_match, t.id)
            if mr is None:
                return HttpResponse(json.dumps({}))
            
            pen_results = mr['PenaltyPlayers'] if 'PenaltyPlayers' in mr else {}
            gk_opponent_surname = ''
            gk_opponent_vote = ''
                
        else: #LIVE
            live_votes, live_teams, already_played_teams = LU.get_live_votes(day)

            votes_home = LU.get_votes(lineup, 
                                    day, 
                                    live_votes=live_votes, 
                                    live_teams=live_teams, 
                                    already_played_teams=already_played_teams, 
                                    my_teamid=None, 
                                    home=True, 
                                    homeAway=None)
            
            votes_opponent = LU.get_votes(opponent_lineup, 
                                    day, 
                                    live_votes=live_votes, 
                                    live_teams=live_teams, 
                                    already_played_teams=already_played_teams,
                                    my_teamid=None,
                                    home=False,
                                    homeAway=None)
                                    
            gk_opponent_surname, gk_opponent_vote = LU.get_goalkeeper_from_votes(votes_opponent)

            penalties_results = LU.calculate_penalties_single_team(lineup, gk_opponent_vote, votes_home)
            pen_results = penalties_results.get('pen_results', {})
        
        return HttpResponse(json.dumps({''
        'teamname': lineup.Team.Name,
        'pen_results': pen_results,
        'gk_opponent_surname': gk_opponent_surname,
        'gk_opponent_vote': gk_opponent_vote
        }))

class GetExtraTimeView(View):
    def get(self, request):
        t = U.get_team_by_name(request.GET['tname'])
        day = request.GET['day']
        competition_id = request.GET['competition']
        lineup = U.get_last_lineup(t, day, comp_id=competition_id)[0]

        live_votes, live_teams, already_played_teams = LU.get_live_votes(day)

        votes_home = LU.get_votes(lineup, 
                                  day, 
                                  live_votes=live_votes, 
                                  live_teams=live_teams, 
                                  already_played_teams=already_played_teams, 
                                  my_teamid=None, 
                                  home=True, 
                                  homeAway=None)


        extra_goals, extra_score, ot_votes_map = LU.calculate_extratime_goals(votes_home, lineup)
        
        return HttpResponse(json.dumps({''
        'teamname': lineup.Team.Name,
        'n_et_goals': extra_goals, 
        'et_score': extra_score, 
        'ot_votes_map': ot_votes_map}))

class MyLiveView(LoginRequiredMixin, View):
    template_name = 'l4m/my_live.html'

    def get(self, request):
        myteam = U.get_user_team(request.user.id)
        current_day = int(U.get_current_day())   
        lineup_couples = []
        overtime, _ = U.check_day_already_started(current_day)
        total_league = U.get_competition('Total League').first()
    
        my_today_couples = LU.get_my_couples_from_calendar(myteam['id'], current_day)

        live_votes, live_teams, already_played_teams = LU.get_live_votes(current_day)

        for c in my_today_couples:
            comp_id = c.CompetitionCalendar.Competition_id
            comp = U.get_competition_by_id(comp_id)
            homeAway=U.get_homeaway(comp_id, current_day)

            if comp_id == total_league.id:
                h_lineup_to_show = LU.get_b11_lineup(c.HomeTeam, current_day, live_votes, live_teams, already_played_teams)
                h_lineup_to_show['t']=c.HomeTeam
                a_lineup_to_show = LU.get_b11_lineup(c.AwayTeam, current_day, live_votes, live_teams, already_played_teams)
                a_lineup_to_show['t']=c.AwayTeam
            else:
                h_lineup_to_show = LU.get_lineup_to_show(c.HomeTeam, current_day, comp_id, overtime)
                a_lineup_to_show = LU.get_lineup_to_show(c.AwayTeam, current_day, comp_id, overtime)

            lineup_couples.append((h_lineup_to_show, a_lineup_to_show, homeAway, comp))

        all_votes = []
        all_comps = []

        for lineup_couple in lineup_couples:
            _homeaway = lineup_couple[2]
            _lineup_comp = lineup_couple[3]

            if _lineup_comp.id == total_league.id:
                votes_home = LU.get_votes_total(lineup_couple[0], home=True, homeAway=_homeaway)
                votes_away = LU.get_votes_total(lineup_couple[1], home=False, homeAway=_homeaway)
            else: 
                votes_home = LU.get_votes(lineup_couple[0], current_day, live_votes, live_teams, already_played_teams=already_played_teams, my_teamid=myteam['id'], homeAway=_homeaway)
                votes_away = LU.get_votes(lineup_couple[1], current_day, live_votes, live_teams, already_played_teams=already_played_teams, my_teamid=myteam['id'], home=False, homeAway=_homeaway)
            
            all_votes.append( \
                [votes_home, votes_away]
            )
            all_comps.append(_lineup_comp)

        params = { 
            'all_votes_comps' : zip(all_votes, all_comps),
            'current_day': current_day,
            }
    
        return render(request, self.template_name, params)

    def post(self, request):
        pass

class LiveB11View(LoginRequiredMixin, View):
    template_name = 'l4m/live_b11.html'

    def get(self, request):
        current_day = U.get_current_day()
        
        team_ids_names = team.Team.objects.values_list("id", "Name")

        live_votes, live_teams, already_played_teams = LU.get_live_votes(int(current_day))
        
        all_best = LU.get_best_11(team_ids_names, int(current_day), live_votes, live_teams, already_played_teams)

        sorted_best = sorted(
            (b for b in all_best if b is not None),
            key=lambda x: x['score'],
            reverse=True
        )
        
        params = {
            'sorted_best': sorted_best
        }

        return render(request, self.template_name, params)

@login_required
def LiveView(request):
    template_name = 'l4m/live.html'

    teamid = U.get_user_team(request.user.id)['id']

    current_day = U.get_current_day()
    all_days = range(1, int(current_day) + 1) #default campionato

    my_series_mainleague = U.get_my_series(teamid, competitionid=1) #default campionato
    my_seriesid_mainleague = my_series_mainleague[0].id

    all_competitions = U.get_all_live_active_competitions()
    today_competitions = U.get_all_today_competitions(current_day)
    today_competitions_ids = [tc.id for tc in today_competitions]

    if(len(request.POST) > 0 and 'jsonData' in request.POST):
        data = json.loads(request.POST['jsonData'])
        competition_id = data['competition']
        seriesid = data['series']
        my_series = U.get_my_series(teamid, competitionid=competition_id)
        if len(my_series) <= 0:
            teamid = None
        elif(seriesid != my_series[0].id):
            teamid = None
        day = int(data['day'])
    else:
        competition_id = 1 #default campionato
        day = int(current_day)
        seriesid = my_seriesid_mainleague

    all_series = U.get_all_series(competitionid=competition_id)
    all_my_series_ids = [s.id for s in U.get_all_my_series(teamid)]
    homeAway=U.get_homeaway(competition_id, day)
    extratime_penalties = U.get_overtime_penalties(competition_id, day)

    series_teams = team.Team.objects.filter(Series__id=seriesid)
    last_lineups_d = {}
    overtime, _ = U.check_day_already_started(day)
    is_live_day = True
    already_played_teams = []

    #QUICK LOAD THE PAST
    if int(day < int(current_day)):
        couples = LU.get_couples_and_matches_from_calendar(seriesid, day, competition_id=competition_id)
        couples = [couples.pop(couples.index(i)) for i in couples if (i[0]==teamid or i[1]==teamid)]+couples #get user match as first
        
        all_votes = []
        mrs = LU.get_matches_results(couples)

        for mr in mrs:
            votes_home = LU.format_votes(mr[0]) #format votes_tit, items, votes_ris
            votes_away = LU.format_votes(mr[1]) #format votes_tit, items, votes_ris

            all_votes.append( \
                    [votes_home, votes_away]
                )
            
        is_live_day = False

    else:
        #get all live players
        live_votes, live_teams, already_played_teams = LU.get_live_votes(day)

        #VALIDO PER:
        # TOTAL LEAGUE
        total_league = all_competitions.get(Name='Total League')
        if competition_id == total_league.id:
            for t in series_teams:
                lineup_to_show = LU.get_b11_lineup(t, day, live_votes, live_teams, already_played_teams)
                lineup_to_show['t']=t
                last_lineups_d[t.id] = lineup_to_show

            couples = LU.get_couples_from_calendar(seriesid, day, competition_id=competition_id)
            couples = [couples.pop(couples.index(i)) for i in couples if (i[0]==teamid or i[1]==teamid)]+couples #get user match as first
            lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]]) for c in couples ]

            all_votes = []

            for lineup_couple in lineup_couples:
                votes_home = LU.get_votes_total(lineup_couple[0], home=True, homeAway=homeAway)
                votes_away = LU.get_votes_total(lineup_couple[1], home=False, homeAway=homeAway)
                all_votes.append( \
                    [votes_home, votes_away]
                )

        else:
            #VALIDO PER:
            #CAMPIONATO
            #COPPA DI LEGA
            #COPPA DI SERIE
            for t in series_teams:
                l = U.get_last_lineup(t, day, comp_id=competition_id)
                if(len(l) <= 0 and overtime): #overtime (day started)
                    last_valid_l = U.get_last_valid_lineup(t)

                lineup_to_show = t.Name #base

                if not overtime:
                    if len(l) > 0:
                        lineup_to_show = l[0]
                    else:
                        lineup_to_show = t.Name

                if overtime and day == int(current_day):
                    if len(l) > 0:
                        lineup_to_show = l[0]
                    else:
                        lineup_to_show = last_valid_l
                        U.save_last_valid_lineup(last_valid_l, day, seriesid)
                        
                else:  #filter for historical data
                    lineup_to_show = l[0] if len(l)> 0 else t.Name #always valued because we SHOULD save the lineup

                last_lineups_d[t.id] = lineup_to_show

            couples = LU.get_couples_from_calendar(seriesid, day, competition_id=competition_id)
            couples = [couples.pop(couples.index(i)) for i in couples if (i[0]==teamid or i[1]==teamid)]+couples #get user match as first
            lineup_couples = [ (last_lineups_d[c[0]], last_lineups_d[c[1]]) for c in couples ]

            all_votes = []

            for lineup_couple in lineup_couples:
                votes_home = LU.get_votes(lineup_couple[0], day, live_votes, live_teams, already_played_teams=already_played_teams, my_teamid=teamid, homeAway=homeAway)
                votes_away = LU.get_votes(lineup_couple[1], day, live_votes, live_teams, already_played_teams=already_played_teams, my_teamid=teamid, home=False, homeAway=homeAway)
                
                #check here for extratime and penalties
                if overtime and extratime_penalties: 
                    if(LU.check_match_for_extratime(lineup_couple[0].Team.id, lineup_couple[1].Team.id, 
                                                 votes_home, votes_away, 
                                                 day, competition_id, seriesid)):
                        votes_home = LU.add_extratime_penalties_flag(votes_home)
                        votes_away = LU.add_extratime_penalties_flag(votes_away)

                all_votes.append( \
                    [votes_home, votes_away]
                )
    
    all_scores = json.dumps([[(v[1][1], v[1][9]) for v in vote] for vote in all_votes]) if overtime else []

    params = { 
        'all_votes' : all_votes, 
        'all_scores' : all_scores,
        'all_series' : all_series,
        'current_competition': competition_id,
        'current_series' : seriesid,
        'all_days' : all_days,
        'current_day': day,
        'all_competitions' : all_competitions,
        'all_my_series_ids' : all_my_series_ids,
        'homeAway': homeAway,
        'is_live_day': is_live_day,
        'today_competitions_ids': today_competitions_ids,
        'extratime_penalties': extratime_penalties,
        }
    
    return render(request, template_name, params)
    
class GetLineupsByTeamView(View):
    
    def post(self, request):
        tname = request.POST['teamname']
        day = request.POST['day']
        seriesid = request.POST['series']
        t = U.get_team_by_name(tname)
        l_ups = U.get_all_lineups(t.id, day, seriesid)

        if len(l_ups) <= 0:
            return HttpResponse()

        #TODO: get by squad, keeping the free players in squad
        pls_map = U.get_players_by_lups(l_ups)
        pls_dict = {}
        for pl in pls_map:
            pls_dict[pl['id']] = [pl['Surname'],pl['Role']]
        json_l_ups = U.cleanJSON(serializers.serialize('json', l_ups))
        return HttpResponse(json.dumps({'map':pls_dict,'l_ups':json_l_ups}))
    
class GetLiveRankingView(View):
    def get(self, request):
        competition_id = request.GET['competition_id']
        seriesid = request.GET['series_id']
        day = request.GET['day']
        all_scores = request.GET['all_scores']
        last_ranking = U.get_last_available_ranking_by_day(competition_id, seriesid, int(day))
    
        if(last_ranking is not None):
            last_ranking = json.loads(last_ranking[0].RankingLine)

        if(all_scores is not None):
            all_scores = json.loads(all_scores)

        live_ranking = LU.create_live_ranking(all_scores, last_ranking)

        return HttpResponse(json.dumps(live_ranking))
        # return HttpResponse(json.dumps({'lines': live_ranking}))