from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Showcase(models.Model):

    Description = models.TextField(max_length=500, null=True, blank=True)
    Season = models.ForeignKey(to=C.Constant_Strings.season, on_delete=models.CASCADE, null=True)
    Competition = models.ForeignKey(to=C.Constant_Strings.competition, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return " ".join([self.Description])
