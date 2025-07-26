from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Real_calendar(models.Model):
    Competition = models.ForeignKey(C.Constant_Strings.competition, on_delete=models.CASCADE)
    Day = models.IntegerField()
    Date = models.DateTimeField()
    RealTeamHome = models.ForeignKey(C.Constant_Strings.real_team, on_delete=models.CASCADE)
    RealTeamAway = models.ForeignKey(C.Constant_Strings.real_team, on_delete=models.CASCADE)
    
    def __str__(self):
        return " ".join([self.Name])
