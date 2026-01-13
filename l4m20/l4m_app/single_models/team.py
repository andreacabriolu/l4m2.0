from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Team(models.Model):
    
    Name = models.CharField(max_length=100)
    Series = models.ManyToManyField(C.Constant_Strings.series)
    Users = models.ManyToManyField(User, related_name='user')
    LogoPath = models.CharField(null=True)
    Competition = models.ManyToManyField(C.Constant_Strings.competition, through=C.Constant_Strings.team_competition)
    
    def __str__(self):
        return " ".join([self.Name])
