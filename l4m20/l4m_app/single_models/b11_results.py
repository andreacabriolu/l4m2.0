from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class B11Results(models.Model):
    Day = models.IntegerField()
    Team = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True)    
    B11Fp = models.FloatField()
    Lineup = models.TextField()
    Module = models.CharField(max_length=3, null=True, blank=True)
    PartialScore = models.FloatField(null=True, blank=True)
    ModifierScore = models.FloatField(null=True, blank=True)
    ModifierTotal = models.FloatField(null=True, blank=True)
    CaptainBonus = models.FloatField(null=True, blank=True)
    AllSixBonus = models.FloatField(null=True, blank=True)
    NoYellowBonus = models.FloatField(null=True, blank=True)
    ModifierFromNoGk = models.BooleanField(default=False)
    Season = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.season, null=True)

    def __str__(self):
        return f"{self.Team} {self.B11Fp} (Day {self.Day})"