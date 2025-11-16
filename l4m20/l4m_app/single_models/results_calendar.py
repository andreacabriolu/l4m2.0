from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Results_Calendar(models.Model):
    
    Day = models.IntegerField()
    TeamHome = models.CharField(max_length=100)
    TeamAway = models.CharField(max_length=100)
    PointsHome = models.IntegerField()
    PointsAway = models.IntegerField()

    def __str__(self):
        return " ".join([self.Name])
