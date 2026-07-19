from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Team_Competition(models.Model):
    
    Team = models.ForeignKey(C.Constant_Strings.team, on_delete=models.CASCADE)
    Competition = models.ForeignKey(C.Constant_Strings.competition, on_delete=models.CASCADE)
    Series = models.ForeignKey(C.Constant_Strings.series, on_delete=models.CASCADE, null=True, blank=True) #optional
    Season = models.ForeignKey(C.Constant_Strings.season, on_delete=models.CASCADE, null=True)
    IsWinner = models.BooleanField(default=False)
    Notes = models.TextField(max_length=500, null=True, blank=True)
    Points = models.IntegerField(null=True, blank=True)
    Position = models.IntegerField(null=True, blank=True)
    Elimination_Stage = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Team', 'Competition', 'Season'], name='unique_team_competition')
        ]  

    def __str__(self):
        return f"{self.Team} - {self.Competition} - {self.Season}"
