from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Real_calendar(models.Model):
    Team_A = models.ForeignKey(C.Constant_Strings.real_team, on_delete=models.CASCADE)
    Team_B = models.ForeignKey(C.Constant_Strings.real_team, on_delete=models.CASCADE)
    Date = models.DateTimeField()
    
    def __str__(self):
        return " ".join([self.Name])
