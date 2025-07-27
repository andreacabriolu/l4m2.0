from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Lineup(models.Model):
    Line = models.CharField()
    Team = models.ForeignKey(to=C.Constant_Strings.team, on_delete=models.CASCADE)
    Version = models.IntegerField()
    Timestamp = models.DateTimeField()
    Series = models.ForeignKey(to=C.Constant_Strings.series, on_delete=models.CASCADE)
    Day = models.IntegerField()
