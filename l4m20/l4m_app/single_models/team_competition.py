from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Team_Competition(models.Model):
    
    Team = models.ForeignKey(C.Constant_Strings.team, on_delete=models.CASCADE)
    Competition = models.ForeignKey(C.Constant_Strings.competition, on_delete=models.CASCADE)
    Elimination_stage = models.CharField(null=True, default='')
