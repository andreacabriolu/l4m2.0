from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from .. import utilities as U
from ..models import *

class RulesView(LoginRequiredMixin, View):
    template_name = 'l4m/rules.html'

    def get(self, request):

        rulesHTML = config.Config.objects.get(Name='RulesHTML')
        
        params = {
            'rulesHTML': rulesHTML.Value
        }

        return render(request, self.template_name, params)

