from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Mark_Players(models.Model):
    
    Market = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.market, null=True)
    Player = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.player, null=True)
    
