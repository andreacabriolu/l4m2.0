from datetime import datetime
from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.db.models import Q

from .. import utilities as U
from ..models import *
from l4m20 import constants as C

class LiveView(LoginRequiredMixin, View):
    template_name = 'l4m/live.html'

    def get(self,request):
        

        params = { 
          }
        
        return render(request, self.template_name, params)
    
