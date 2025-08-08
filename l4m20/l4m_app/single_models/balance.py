from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Balance(models.Model):
    Name = models.CharField(max_length=100)
    Wages_amount = models.IntegerField()
    Purchases_amount = models.IntegerField()
    Wages_max = models.IntegerField(null=True)
    Purchases_max = models.IntegerField(null=True)
    Team = models.ForeignKey(C.Constant_Strings.team, on_delete=models.CASCADE, null=True)
    N_carognate = models.IntegerField(null=True, default=0)
    
    def __str__(self):
        return " ".join([self.Name])
