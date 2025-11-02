from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .. import utilities as U
from .. import calculate_utilities as CU
from ..models import *

class CalculateView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/calculate.html'

    def get(self,request):

        all_competitions = U.get_all_active_competitions()
        current_day = U.get_current_day() #TODO: per competition?
        
        params = {
            'all_competitions': all_competitions,
            'current_day': current_day,
        }
        
        return render(request, self.template_name, params)
    
class GetCurrentDayByCompetition(View):
    def post(self, request):
        #TODO: filter by competition!
        competition_id = request.POST['competitionid']
        c = competition.Competition.objects.get(pk=int(competition_id))
        if c is None:
            return HttpResponse('error: no competition found')

        current_day = U.get_current_day(c.Name)

        return HttpResponse(current_day)
    
class CalculateDayView(View):
    def post(self, request):

        #TODO: write in:
        # calendar (NEW)

        try:

            competitionid = request.POST['competitionid']
            day = request.POST['day']
            all_comp = eval(request.POST['all_comp'].capitalize())

            main_league = U.get_competition(name='Campionato')[0]
            b11_league = U.get_competition(name='Best 11')[0]
            cdl_league = U.get_competition(name='Coppa di Lega')[0]

            if all_comp:
                CU.calculate_league(main_league, day)
                CU.calculate_league(cdl_league, day)
                CU.calculate_b11_league(b11_league, day)
                return HttpResponse('GIORNATA CALCOLATA PER TUTTE LE COMPETIZIONI')

            else: 
                if int(competitionid) == main_league.id:
                    CU.calculate_league(main_league, day)
                    return HttpResponse(f'GIORNATA CALCOLATA PER {main_league.Name}')

                if int(competitionid) == cdl_league.id:
                    CU.calculate_league(cdl_league, day)
                    return HttpResponse(f'GIORNATA CALCOLATA PER {cdl_league.Name}')

                if int(competitionid) == b11_league.id:
                    CU.calculate_b11_league(b11_league, day)
                    return HttpResponse(f'GIORNATA CALCOLATA PER {b11_league.Name}')
            
                return HttpResponse('GIORNATA NON CALCOLATA, COMPETIZIONE NON TROVATA')

        except Exception as e:
            return HttpResponse(f'error {e}')
        
class SetDayView(View):
    def post(self, request):
        c_day = request.POST['day']
        config_day = config.Config.objects.filter(Name="CurrentDay").first()
        config_day.Value = c_day
        config_day.save()

        return HttpResponse(c_day)
