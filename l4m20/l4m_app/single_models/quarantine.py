from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Quarantine(models.Model):
    Player = models.ForeignKey(to=C.Constant_Strings.player, on_delete=models.CASCADE)
    Date = models.DateField(auto_now_add=True)
    QuarantinableUntil = models.DateField()

    def __str__(self):
        return " ".join([self.Player.Name, self.QuarantinableUntil.__str__()])
