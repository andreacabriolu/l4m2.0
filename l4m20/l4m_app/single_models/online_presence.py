from l4m20 import constants as C
from django.db import models
from django.contrib.auth.models import User

class OnlinePresence(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="online_presence"
    )

    last_seen = models.DateTimeField(
        auto_now=True
    )