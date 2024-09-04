from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.views import View, generic
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import datetime

import pytz 

from . import utilities as U
from .models import *


class LoginView(View):
    template_name= 'l4m/login.html'
    
    def get(self,request):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form':form})
    
    def post(self, request):
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/l4m/') #TODO: redirect based on roles!
        else:
            return render(request, self.template_name, {'form': form})
        
class IndexView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/index.html'
    login_url = '/login/'

    def get(self,request):

        players_gk = player.Player.objects.filter(Role="P").select_related('RealTeam').values('id','Surname','Role','RealTeam__Name')
        params = { 
            'players_gk':players_gk
          }
        
        return render(request, self.template_name, params)
    
class SendBetView(View):
    template_name = 'l4m/index.html'

    def post(self, request): 
        data = json.loads(request.POST.get("jsonData"))
        if (data is None): return
        
        bet_obj =  bet.Bet_Obj()
        bet_obj.Amount = int(data['betamount'])
        bet_obj.Player = data['playerid']
        # bet_obj.Expiration_Date = U.calculate_expiration(datetime.datetime.now(tz=pytz.UTC)) #TODO: exclude nighttime
        bet_obj.Expiration_Date = data['exp_date']

        player_ = get_object_or_404(player.Player, id=bet_obj.Player)
        bet_new = bet.Bet(Amount=bet_obj.Amount,
                          Player = player_,
                          Best=True,
                          Expiration_Date=bet_obj.Expiration_Date.__str__())
        bet_new.save()

        params = {}

        return render(request, self.template_name, params)