from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Competition(models.Model):
    
    Name = models.CharField(max_length=100)
    
    def __str__(self):
        return " ".join([self.Name])
