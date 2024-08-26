from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class RealTeam(models.Model):

    STATUSES = (("A", _("Serie A")),
                ("B", _("Altra serie")),
                )
    
    Name = models.CharField(max_length=100)
    Status = models.CharField(max_length=1, choices=STATUSES)
    
    def __str__(self):
        return " ".join([self.Name])
