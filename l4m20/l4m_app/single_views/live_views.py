from django.core import serializers
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json


from .. import utilities as U
from .. import live_utilities as LU
from ..models import *

class MyLiveView(View):
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

        live_votes, live_teams, already_played_teams = LU.get_live_votes(current_day)
        
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

    series_teams = team.Team.objects.filter(Series__id=seriesid)
    last_lineups_d = {}
    overtime, _ = U.check_day_already_started(day)

    #get all live players
    live_votes, live_teams, already_played_teams = LU.get_live_votes(day)

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

    else:
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
                if(len(l) <= 0 and overtime): #overtime
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
                        U.save_last_valid_lineup(last_valid_l, day)
                        U.update_balance(t.id)
                        
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
                all_votes.append( \
                    [votes_home, votes_away]
                )
        
    params = { 
        'all_votes' : all_votes,
        'all_series' : all_series,
        'current_competition': competition_id,
        'current_series' : seriesid,
        'all_days' : all_days,
        'current_day': day,
        'all_competitions' : all_competitions,
        'all_my_series_ids' : all_my_series_ids,
        'homeAway': homeAway,
        'today_competitions_ids': today_competitions_ids
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