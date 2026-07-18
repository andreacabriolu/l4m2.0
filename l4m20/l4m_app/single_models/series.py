from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Series(models.Model):
    Name = models.CharField(max_length=100)
    Competition = models.ForeignKey(to=C.Constant_Strings.competition, on_delete=models.CASCADE, null=True)
    Active = models.BooleanField(default=True)
    IsGirone = models.BooleanField(default=True)
    Season = models.ForeignKey(to=C.Constant_Strings.season, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return " ".join([self.Name, str(self.Competition), str(self.Season)])
