from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class CompetitionCalendar(models.Model):

    Competition = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.competition, null=True)
    Day = models.IntegerField()              # day of play
    Stage = models.CharField(max_length=50)
    HomeAway = models.BooleanField(default=False)
    Overtime = models.BooleanField(default=False)
    Penalties = models.BooleanField(default=False)
    Suspended = models.BooleanField(default=False)
    Num_Matches = models.IntegerField(default=None, null=True)

    def __str__(self):
        return f"{self.Competition} - Giornata {self.Day} - {self.Stage}"


    class Meta:
        db_table = 'l4m_app_competition_calendar' 
