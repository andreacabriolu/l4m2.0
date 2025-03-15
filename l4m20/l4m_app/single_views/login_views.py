
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from ..single_models import team, balance
from datetime import datetime

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
        #TODO: find user team here
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/l4m/') #TODO: redirect based on roles!
        else:
            return render(request, self.template_name, {'form': form})
        
class LogoutView(View):
    template_name= 'l4m/login.html'
    form = AuthenticationForm()

    def get(self,request):
        logout(request)
        return redirect('/login/', self.form)
    
class RegisterView(View):
    template_name = 'l4m/register.html'

    def get(self,request):
        return render(request, self.template_name)

    def post(self, request):
        new_user = {}
        form = AuthenticationForm()

        new_user['username'] = request.POST['username']
        new_user['email'] = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if(password1 != password2): #TODO: use built in pwd validation
            return render(request, self.template_name, {'res':'ERROR CREATING USER'})
        
        new_user['password'] = password1

        user = User.objects.create_user(username=new_user['username'], password=new_user['password'])
        user.set_password(new_user['password'])
        user.save()

        new_team = request.POST['team']
        _team =  team.Team.objects.create(Name=new_team)
        _team.Users.set([user])
        _team.save()

        _bal = balance.Balance.objects.create(
            Name=f'newbal_{datetime.now.__str__()}',
            Wages_amount = 300,
            Purchases_amount = 300,
            Team = _team
            )
        _bal.save()

        return redirect('/login/', form)