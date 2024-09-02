from django.contrib import admin
from .models import player, real_team

# Register your models here.

admin.site.register(player.Player)
admin.site.register(real_team.RealTeam)
