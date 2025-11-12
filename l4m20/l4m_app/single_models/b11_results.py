from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class B11Results(models.Model):
    Day = models.IntegerField()
    Team = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True)    
    B11Fp = models.FloatField()

    def __str__(self):
        return f"{self.Team} {self.Fp}"