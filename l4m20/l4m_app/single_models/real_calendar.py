from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Real_calendar(models.Model):
    # Competition = models.ForeignKey(C.Constant_Strings.competition, on_delete=models.CASCADE)
    Day = models.IntegerField()
    Date = models.DateTimeField()
    RealTeamHome = models.ForeignKey(C.Constant_Strings.real_team, on_delete=models.CASCADE, related_name="team_home")
    RealTeamAway = models.ForeignKey(C.Constant_Strings.real_team, on_delete=models.CASCADE, related_name="team_away")
    FT = models.BooleanField(default=False) #full time flag, to know if the match has been played or not
    
    def __str__(self):
       return f"Day {self.Day}:{self.RealTeamHome.Name} vs {self.RealTeamAway.Name}"
