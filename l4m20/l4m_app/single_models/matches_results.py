from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class MatchesResults(models.Model):

    MatchesCalendar = models.ForeignKey(on_delete=models.CASCADE,to='l4m_app.MatchesCalendar', null=True)
    Team = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True)    
    Fp = models.FloatField()    # Fp
    FpO = models.FloatField(null=True)    # Fp Overtime
    Pen = models.IntegerField(null=True)    # Penalties

    def __str__(self):
        return f"{self.MatchesCalendar} | {self.Team} {self.Fp}"

    class Meta:
        db_table = 'l4m_app_matches_results' 
