from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.views import View, generic
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, View):
    #TODO: implement control on user passes test (https://docs.djangoproject.com/en/4.2/topics/auth/default/#limiting-access-to-logged-in-users-that-pass-a-test)
    template_name = 'l4m/index.html'
    login_url = '/login/'

    def get(self,request):
        params = {
            }
        return render(request, self.template_name, params)

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
            return render(request, self.template, {'form': form})
        