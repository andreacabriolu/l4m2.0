from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class PlayerStatistics(models.Model):
    Player = models.ForeignKey(to=C.Constant_Strings.player, on_delete=models.CASCADE, null=True)
    Birthdate = models.DateField(null=True, blank=True)
    Nationality = models.CharField(max_length=100, null=True, blank=True)
    Role = models.CharField(max_length=50, null=True, blank=True)
    Fantamedia = models.FloatField(null=True, blank=True)
    Media = models.FloatField(null=True, blank=True)
    Goals = models.IntegerField(null=True, blank=True)
    Assists = models.IntegerField(null=True, blank=True)
    Yellow_Cards = models.IntegerField(null=True, blank=True)
    Red_Cards = models.IntegerField(null=True, blank=True)
    Matches_Played = models.IntegerField(null=True, blank=True)
    Goals_Conceded = models.IntegerField(null=True, blank=True)
    Clean_Sheets = models.IntegerField(null=True, blank=True)
    Penalties_Saved = models.IntegerField(null=True, blank=True)
    Penalties_Missed = models.IntegerField(null=True, blank=True)
    Penalties_Scored = models.IntegerField(null=True, blank=True)
    Own_Goals = models.IntegerField(null=True, blank=True)
    Penalties_Procured = models.IntegerField(null=True, blank=True)
    Substitutions_In = models.IntegerField(null=True, blank=True)
    Substitutions_Out = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return "Statistics_".join([self.Player])