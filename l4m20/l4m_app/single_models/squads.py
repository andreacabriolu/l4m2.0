from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _

class Squads(models.Model):
    
    Team = models.ForeignKey(on_delete=models.PROTECT, to=C.Constant_Strings.team, null=False,default=0)
    Amount = models.IntegerField(default=0,null=False)
    Player = models.ForeignKey(on_delete=models.PROTECT, to=C.Constant_Strings.player, null=False,default=0)
    Last_bet = models.ForeignKey(on_delete=models.PROTECT, to=C.Constant_Strings.bet, null=True)
    Salary = models.IntegerField(null=True)
    Years = models.IntegerField(null=True)
    Jersey_num = models.IntegerField(null=True)
    Quot = models.IntegerField(null=True)
    Quarantine = models.BooleanField(default=False)
    Suspended = models.BooleanField(default=False)
    

class Squads_Obj():
    Team=str
    Amount=int
    Player=int
    Last_bet=int
    Salary=int
    Years=int
    Jersey_num=int
    Quot=int
    Quarantine=bool
    Suspended=bool
