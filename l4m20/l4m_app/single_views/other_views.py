from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from l4m_app.single_models import other_competition

class OtherView(LoginRequiredMixin, View):
    template_name = "l4m/other.html"

    def get(self, request, other_competition_id=None):
        other_comp = other_competition.OtherCompetition.objects.filter(id=other_competition_id).first()
        if other_comp is not None:
            comp = {
                'logo_path': other_comp.LogoPath,
                'name': other_comp.Name,
                'description': other_comp.Description,
            }

        params = {
            'comp': comp,
        }
        return render(request, self.template_name, params)