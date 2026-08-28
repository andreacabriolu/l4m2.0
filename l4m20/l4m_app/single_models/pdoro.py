from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Pdoro(models.Model):
    Team = models.ForeignKey(to=C.Constant_Strings.team, on_delete=models.CASCADE)
    Day = models.IntegerField()
    Season = models.ForeignKey(to=C.Constant_Strings.season, on_delete=models.CASCADE)
    C1 = models.FloatField()
    C2 = models.FloatField()
    C3 = models.FloatField()
    Pts = models.FloatField()


    def __str__(self):
        return " ".join([self.Team.Name, self.Day.__str__(), self.Season.Name])
