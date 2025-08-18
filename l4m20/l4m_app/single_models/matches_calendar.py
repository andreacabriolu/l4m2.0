from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class MatchesCalendar(models.Model):

    CompetitionCalendar = models.ForeignKey(on_delete=models.CASCADE,to='l4m_app.CompetitionCalendar', null=True)
    HomeTeam = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True, related_name='home_team')
    AwayTeam = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True, related_name='away_team')    

    def __str__(self):
        return f"{self.CompetitionCalendar} | {self.HomeTeam}- {self.AwayTeam})"

    class Meta:
        db_table = 'l4m_app_matches_calendar' 
