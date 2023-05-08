from django.db import models

from dirupl.common.models import UUIDModel
from dirupl.address_directory.managers import CredentialManager


class Credential(UUIDModel):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True)
    keys_private = models.CharField(max_length=255)
    keys_public = models.CharField(max_length=255)
    keys_secret = models.CharField(max_length=255)
    fcm_token = models.CharField(max_length=255)
    fcm_pushset = models.CharField(max_length=255)
    gcm_token = models.CharField(max_length=255)
    gcm_androidid = models.BigIntegerField()
    gcm_securitytoken = models.BigIntegerField()
    gcm_appid = models.CharField(max_length=255)

    objects = CredentialManager()