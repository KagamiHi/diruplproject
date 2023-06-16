from django.db import models

from dirupl.common.models import UUIDModel
from dirupl.address_directory.managers import GuildinfoManager


class Guildinfo(UUIDModel):
    _guild_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(default = 'Unknown', max_length=255)
    inviter_id = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=255)
    members = models.ManyToManyField("users.CustomUser")
    server = models.ForeignKey(
        "address_directory.Server", 
        default = None, 
        on_delete=models.SET_NULL, 
        null=True
        )
    notification_settings = models.ForeignKey(
        "address_directory.NotificationSettings", 
        default = None, 
        on_delete=models.SET_NULL, 
        null=True
        )

    objects = GuildinfoManager()

    @property
    def guild_id(self):
        return int(self._guild_id)