from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Config(models.Model):
    Name = models.CharField()
    Value = models.CharField()
    
    def __str__(self):
        return f"config_{self.Name}"
