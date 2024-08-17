from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    ROLES = (("PT", _("Portiere")), 
            ("DF", _("Difensore")), 
            ("CC", _("Centrocampista")), 
            ("AT", _("Attaccante")),)
    
    Name = models.CharField(max_length=100)
    Surname = models.CharField(max_length=100)
    Role = models.CharField(max_length=2, choices=ROLES)
    
    def __str__(self):
        #TODO: ID player for identifying
        return " ".join([self.Name, self.Surname])
