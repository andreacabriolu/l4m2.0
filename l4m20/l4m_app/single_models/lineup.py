from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Lineup(models.Model):
    Line = models.CharField(max_length=2000)
    Team = models.ForeignKey(to=C.Constant_Strings.team, on_delete=models.CASCADE)
    Version = models.IntegerField()
    Timestamp = models.DateTimeField()
    Series = models.ForeignKey(to=C.Constant_Strings.series, on_delete=models.CASCADE)
    Day = models.IntegerField()
    HideLineup = models.BooleanField(default=False)
    ModNoGk = models.BooleanField(default=False)

    def __str__(self):
        return " ".join([self.Team.Name, self.Day.__str__(), self.Series.Name])
