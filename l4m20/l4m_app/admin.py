from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(player.Player)
admin.site.register(real_team.RealTeam)
admin.site.register(bet.Bet)
admin.site.register(competition.Competition)
admin.site.register(market.Market)
admin.site.register(series.Series)
admin.site.register(session.Session)
admin.site.register(team.Team)
