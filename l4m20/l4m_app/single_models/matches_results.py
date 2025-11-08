from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class MatchesResults(models.Model):

    MatchesCalendar = models.ForeignKey(on_delete=models.CASCADE,to='l4m_app.MatchesCalendar', null=True)
    Team = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True)    
    Fp = models.FloatField()    # Fp
    FpO = models.FloatField(null=True)    # Fp Overtime
    Pen = models.IntegerField(null=True)    # Penalties
    Votes_Tit = models.CharField(null=True)
    Votes_Ris = models.CharField(null=True)
    Home = models.BooleanField(default=False, null=True)
    PartialScore = models.FloatField(null=True)
    ModifierVal = models.FloatField(null=True)
    ModifierScore = models.FloatField(null=True)
    BonusCap = models.FloatField(null=True)
    BonusDisc = models.FloatField(null=True)
    BonusPrest = models.FloatField(null=True)
    GrandTotal = models.FloatField(null=True)
    NGoals = models.IntegerField(null=True)
    Module = models.CharField(null=True)
    OrigModule = models.CharField(null=True)
    ModNoGk = models.BooleanField(null=True)
    MissingSlots = models.IntegerField(null=True)
    Version = models.IntegerField(null=True)
    BonusHome = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.MatchesCalendar} | {self.Team} {self.Fp}"

    class Meta:
        db_table = 'l4m_app_matches_results' 
