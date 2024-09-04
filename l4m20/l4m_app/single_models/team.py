from l4m20 import constants as C
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User


class Team(models.Model):
    
    Name = models.CharField(max_length=100)
    Series = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.series, null=True)
    Session = models.ForeignKey(on_delete=models.CASCADE, to=C.Constant_Strings.session, null=True)
    Users = models.ManyToManyField(User, related_name='user')
    
    def __str__(self):
        return " ".join([self.Name])
