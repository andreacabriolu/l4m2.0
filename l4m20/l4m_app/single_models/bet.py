from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _

class Bet(models.Model):
    
    Time = models.DateTimeField(auto_now=True)
    Amount = models.IntegerField()
    Best = models.BooleanField(default=False)
    Ghost = models.BooleanField(default=False)
    Carognata = models.BooleanField(default=False)
    Player = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.player, null=True)
    Market = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.market, null=True)
    Team = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.team, null=True)
    Session = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.session, null=True)
    Expiration_Date = models.DateTimeField()
    Slot = models.TextField(max_length=2)
    
    def __str__(self):
        return " ".join([self.Time+self.Player])

class Bet_Obj():
    Name=str
    Time=str
    Amount=int
    Best=bool
    Ghost=bool
    Carognata=bool
    Player=str
    Market=str
    Team=str
    Session=str
    Expiration_Date=str
    Slot=str
