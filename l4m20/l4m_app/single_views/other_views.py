import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from .. import utilities as U
from django.db.models import Q

from l4m_app.single_models import matches_results, other_competition, team

def get_angel_butcher_data():
    angel_butcher_data = []
    teams = team.Team.objects.filter(Active=True).values('id','Name')

    for _team in teams:
        team_matches = matches_results.MatchesResults.objects.filter(
            Q(Team_id=_team['id']) & \
            Q(MatchesCalendar__CompetitionCalendar__Competition__Name="Campionato") &
            Q(MatchesCalendar__CompetitionCalendar__Season__Active=True))\
            .select_related('MatchesCalendar','CompetitionCalendar')\
            .values('Votes_Tit')
        
        yel_tot = 0
        red_tot = 0
        for m in team_matches:
            votes_tit = U.cleanJSON(m['Votes_Tit'])
            votes_tit = votes_tit.replace("\"int\"","")
            votes_tit = votes_tit.replace("\"str\"","")
            if votes_tit is not None:
                v_j = json.loads(votes_tit)
                #sum the yel and red cards
                yel_totday = sum (p['yel'] for p in v_j)
                red_totday = sum (p['red'] + p['yelred'] for p in v_j)
                yel_tot += yel_totday
                red_tot += red_totday
            
        angel_butcher_data.append({
            'team_name': _team['Name'],
            'yel_tot': yel_tot,
            'red_tot': red_tot,
            'total': yel_tot + red_tot
        })

    #sort by total and then by red cards
    angel_butcher_data.sort(key=lambda x: (x['total'], x['red_tot']), reverse=True)

    return angel_butcher_data

class AngelButcherView(LoginRequiredMixin, View):
    template_name = "l4m/angel_butcher.html"

    def get(self, request):

        angel_comp = other_competition.OtherCompetition.objects.filter(Name="Angelo e Macellaio").first()

        if angel_comp is not None:
            comp_info = {
                'logo_path': angel_comp.LogoPath,
                'name': angel_comp.Name,
                'description': angel_comp.Description,
            }
        else:
            comp_info = {
                'logo_path': '',
                'name': 'Angelo e Macellaio',
                'description': 'Descrizione Angelo e Macellaio.'
            }

        angel_butcher_data = get_angel_butcher_data()

        params = {
            'comp_info': comp_info,
            'angel_butcher_data': angel_butcher_data,
        }

        return render(request, self.template_name, params)

def get_route66_data():
    r66_data = []
    teams = team.Team.objects.filter(Active=True).values('id','Name')

    for _team in teams:
        team_matches = matches_results.MatchesResults.objects.filter(
            Q(Team_id=_team['id']) & 
            Q(MatchesCalendar__CompetitionCalendar__Competition__Name="Campionato") &
            Q(MatchesCalendar__CompetitionCalendar__Season__Active=True)
        )\
        .select_related('MatchesCalendar','CompetitionCalendar').values('MatchesCalendar__CompetitionCalendar__Day', 'Team_id', 'Fp').order_by('MatchesCalendar__CompetitionCalendar__Day')

        team_data = {
            'team_name': _team['Name'],
            'scores': [m['Fp'] for m in team_matches],
            'days': [{'score': m['Fp'], 'win': m['Fp'] >= 66} for m in team_matches],
        }

        team_data['perfect'] = all(day['win'] for day in team_data['days'])

        r66_data.append(team_data)

    return r66_data
        
class Route66View(LoginRequiredMixin, View):
    template_name = "l4m/route66.html"

    def get(self, request):
        r66_comp = other_competition.OtherCompetition.objects.filter(Name="Route 66").first()

        if r66_comp is not None:
            comp_info = {
                'logo_path': r66_comp.LogoPath,
                'name': r66_comp.Name,
                'description': r66_comp.Description,
            }
        else:
            comp_info = {
                'logo_path': '',
                'name': 'Route 66',
                'description': 'Descrizione R66.'
            }

        r66_data = get_route66_data()

        params = {
            'comp_info': comp_info,
            'r66_data': r66_data,
            'days': range(1, int(U.get_current_day()))
        }

        return render(request, self.template_name, params)