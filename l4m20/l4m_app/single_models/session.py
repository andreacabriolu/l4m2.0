from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Session(models.Model):
    Name = models.CharField(max_length=100)
    Nsvincoli = models.IntegerField()
    Ncarognate = models.IntegerField()
    Market = models.ForeignKey(C.Constant_Strings.market, on_delete=models.CASCADE, null=True)
    Begin = models.DateTimeField(null=True)
    End = models.DateTimeField(null=True)

    def __str__(self):
        return " ".join([self.Name])
