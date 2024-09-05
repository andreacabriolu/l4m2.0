from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Player(models.Model):
    ROLES = (("PT", _("Portiere")), 
            ("DF", _("Difensore")), 
            ("CC", _("Centrocampista")), 
            ("AT", _("Attaccante")),)
    
    STATUSES = (("A", _("Active")),
                ("E", _("Estero")),
                )
    
    Name = models.CharField(max_length=100, null=True)
    Surname = models.CharField(max_length=100)
    Role = models.CharField(max_length=2, choices=ROLES)
    Status = models.CharField(max_length=1, choices=STATUSES)
    RealTeam = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.real_team, null=True)
    Team = models.ForeignKey(on_delete=models.CASCADE,to=C.Constant_Strings.team, null=True)
    
    # def __str__(self):
    #     #TODO: ID player for identifying
    #     return " ".join([self.Name, self.Surname])
