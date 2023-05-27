from django.db import models

from dirupl.common.models import UUIDModel


class NotificationSettings(UUIDModel):
    check_time = models.BooleanField(default = False)
    