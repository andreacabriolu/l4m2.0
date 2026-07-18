from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Ranking(models.Model):
    RankingLine = models.CharField()
    Competition = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.competition, null=True)    
    Series = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.series, null=True)    
    Day = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.Competition.Name}-{self.Series.Season.Name}-Day {self.Day}"
