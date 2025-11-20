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
admin.site.register(real_calendar.Real_calendar)
admin.site.register(matches_calendar.MatchesCalendar)
admin.site.register(matches_results.MatchesResults)
admin.site.register(team.Team)
admin.site.register(balance.Balance)
admin.site.register(bet_history.Bet_History)
admin.site.register(notification.Notification)
admin.site.register(squads.Squads)
admin.site.register(vote.Vote)
admin.site.register(config.Config)
admin.site.register(lineup.Lineup)
admin.site.register(ranking.Ranking)
admin.site.register(team_competition.Team_Competition)