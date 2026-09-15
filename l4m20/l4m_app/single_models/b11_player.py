from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _
from l4m_app.single_models.b11_results import B11Results


class B11Player(models.Model):
    Result = models.ForeignKey(
        B11Results,
        on_delete=models.CASCADE,
        related_name="players"
    )

    Player = models.ForeignKey(
        C.Constant_Strings.player,
        on_delete=models.CASCADE
    )

    Vote = models.FloatField(null=True, blank=True)
    TotVote = models.FloatField(null=True, blank=True)

    Position = models.PositiveSmallIntegerField(null=True, blank=True) #?

    Captain = models.BooleanField(default=False)