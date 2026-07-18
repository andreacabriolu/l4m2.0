from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _


class Season(models.Model):
    Name = models.CharField(max_length=100)
    Start = models.DateField(null=True)
    End = models.DateField(null=True)
    Active = models.BooleanField(default=False)

    def __str__(self):
        return f"season_{self.Name}"
