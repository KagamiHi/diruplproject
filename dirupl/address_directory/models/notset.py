from django.db import models

from dirupl.common.models import UUIDModel


class NotificationSettings(UUIDModel):
    check_time = models.BooleanField(default = False)
    last_message_time = models.PositiveBigIntegerField(default=1, blank=True, null=True)
    show_location = models.BooleanField(default = False)
    show_distance = models.BooleanField(default = False)