from l4m20 import constants as C
from django.db import models
from django.conf import settings


class Notification(models.Model):
    Text = models.CharField(max_length=1000)
    User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

