import json
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
        current_day = U.get_current_day()
        team_comps_lineups = U.get_day_comps_lineups(current_day)
        
        params = {
            'all_competitions': all_competitions,
            'current_day': current_day,
            'team_comps_lineups': team_comps_lineups
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

        try:

            competitionid = request.POST['competitionid']
            day = request.POST['day']
            all_comp = eval(request.POST['all_comp'].capitalize())
            is_day_completed, json_day = U.is_current_day_completed()
            curr_day = U.get_current_day()

            if day == curr_day and not is_day_completed:
                return HttpResponse(f'error GIORNATA {day} ANCORA IN CORSO!')
            
            if day == curr_day and int(day) > int(json_day):
                return HttpResponse(f'error DATI FANTAMASTER NON ANCORA DISPONIBILI PER LA GIORNATA {day}')

            main_league = U.get_competition(name='Campionato')[0]
            b11_league = U.get_competition(name='Best 11')[0]
            cdl_league = U.get_competition(name='Coppa di Lega')[0]
            total_league = U.get_competition(name='Total League')[0]
            cds_seriea_league = U.get_competition(name='Coppa Serie A')[0]
            cds_serieb_league = U.get_competition(name='Coppa Serie B')[0]
            cds_seriec_league = U.get_competition(name='Coppa Serie C')[0]
            pdoro = U.get_competition(name="Panchina d'Oro")[0]

            if all_comp:
                CU.calculate_league(main_league, day)
                CU.calculate_league(cdl_league, day)
                CU.calculate_b11_league(b11_league, day)
                CU.calculate_total_league(total_league, day)
                CU.calculate_league(cds_seriea_league, day)
                CU.calculate_league(cds_serieb_league, day)
                CU.calculate_league(cds_seriec_league, day)
                CU.calculate_pdoro(pdoro, day)
                return HttpResponse('GIORNATA CALCOLATA PER TUTTE LE COMPETIZIONI')

            else: 
                if int(competitionid) == b11_league.id:     
                    CU.calculate_b11_league(b11_league, day)
                    return HttpResponse(f'GIORNATA CALCOLATA PER {b11_league.Name}')
                
                if int(competitionid) == total_league.id:
                    CU.calculate_total_league(total_league, day)
                    return HttpResponse(f'GIORNATA CALCOLATA PER {total_league.Name}')
                
                _competition = competition.Competition.objects.get(pk=competitionid)
                if _competition is not None:
                    CU.calculate_league(_competition, day)
                    return HttpResponse(f'GIORNATA CALCOLATA PER {_competition.Name}')

                else:        
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
    
class GetMissingLineupsView(View):
    def get(self, request):
        t_id = request.GET['t_id']
        day = request.GET['day']

        my_lups = U.get_my_lineups_competitions_by_day(t_id, day)
        my_active_comps = U.get_my_lineup_competitions_from_calendar(t_id, day)

        my_lup_ids = [v['Series_id__Competition_id'] for v in my_lups.distinct()]
        my_comp_ids = [v.id for v in my_active_comps]
        missing_comps = list(set(my_comp_ids)-set(my_lup_ids))

        ret_dict = {
            'filled_comps_names' : [U.get_competition_by_id(filled_comp).Name for filled_comp in my_lup_ids],
            'missing_comps_names' : [U.get_competition_by_id(missing_comp).Name for missing_comp in missing_comps]
        }

        return HttpResponse(json.dumps(ret_dict))

