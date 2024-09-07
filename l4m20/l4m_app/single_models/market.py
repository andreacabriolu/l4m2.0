from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Market(models.Model):

    STATUSES = (("O", _("Aperto")),
                ("C", _("Chiuso")),
                )
    
    Name = models.CharField(max_length=100)
    Status = models.CharField(max_length=1, choices=STATUSES)
    Competition = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.competition, null=True)
    
    def __str__(self):
        return " ".join([self.Name])
