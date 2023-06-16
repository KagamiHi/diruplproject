from django.db import models

from dirupl.common.models import UUIDModel


class NotificationSettings(UUIDModel):
    check_time = models.BooleanField(default = False)
    last_message_time = models.PositiveBigIntegerField(default=1, blank=True, null=True)
    event_show_location = models.BooleanField(default = False)
    event_show_distance = models.BooleanField(default = False)
    vend_show_location = models.BooleanField(default = False)
    vend_show_distance = models.BooleanField(default = False)


    def __str__(self):
        return f"event show location:{self.event_show_location},event show distance:{self.event_show_distance}, vend show location:{self.vend_show_location},vend show distance:{self.vend_show_distance}"