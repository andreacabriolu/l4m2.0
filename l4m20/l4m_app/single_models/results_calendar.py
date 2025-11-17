from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Results_Calendar(models.Model):
    
    Day = models.IntegerField()
    TeamHome = models.ForeignKey(C.Constant_Strings.team, on_delete=models.CASCADE, related_name='rc_home_team')
    TeamAway = models.ForeignKey(C.Constant_Strings.team, on_delete=models.CASCADE, related_name='rc_away_team')
    PointsHome = models.IntegerField()
    PointsAway = models.IntegerField()

    def __str__(self):
        return " ".join([self.Name])
