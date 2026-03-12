from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from .. import utilities as U
from django.db.models import Q

from l4m_app.single_models import matches_results, other_competition, team

def get_route66_data():
    r66_data = []
    teams = team.Team.objects.filter(Active=True).values('id','Name')

    for _team in teams:
        team_matches = matches_results.MatchesResults.objects.filter(Q(Team_id=_team['id']) & Q(MatchesCalendar__CompetitionCalendar__Competition__Name="Campionato"))\
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

        r66_data = get_route66_data()

        params = {
            'comp_info': comp_info,
            'r66_data': r66_data,
            'days': range(1, int(U.get_current_day()))
        }

        return render(request, self.template_name, params)