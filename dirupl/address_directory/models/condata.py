from django.db import models
from django.utils import timezone

from dirupl.common.models import UUIDModel
from dirupl.address_directory.managers import ServerManager


class Server(UUIDModel):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE)
    server_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255)
    desc = models.TextField(blank=True, null=True)
    url = models.URLField(max_length=200)
    img = models.URLField(max_length=200)
    logo = models.URLField(max_length=200)
    ip = models.CharField(max_length=255)
    _playerid = models.CharField(max_length=255)
    _playertoken = models.CharField(max_length=255)
    port = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)

    objects = ServerManager()

    class Meta:
        ordering = ['date_created']

    def __str__(self):
        return self.name
    
    @property
    def playerid(self):
        return int(self._playerid)
    
    @property
    def playertoken(self):
        return int(self._playertoken)
    