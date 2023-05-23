from django.db import models

from dirupl.common.models import UUIDModel
from dirupl.address_directory.managers import CredentialManager


class Credential(UUIDModel):
    user = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, null=True, blank=True, unique=True)
    keys_private = models.CharField(max_length=255)
    keys_public = models.CharField(max_length=255)
    keys_secret = models.CharField(max_length=255)
    fcm_token = models.CharField(max_length=255)
    fcm_pushset = models.CharField(max_length=255)
    gcm_token = models.CharField(max_length=255)
    gcm_androidid = models.CharField(max_length=255)
    gcm_securitytoken = models.CharField(max_length=255)
    gcm_appid = models.CharField(max_length=255)
    rust_registration_status = models.BooleanField(default = False)

    objects = CredentialManager()

    async def fcm_credentials_to_dict(self):
        return {
            'gcm':{
                'token':self.gcm_token,
                'appId':self.gcm_appid,
                'androidId':self.gcm_androidid,
                'securityToken':self.gcm_securitytoken
            },
            'keys':{
                'public':self.keys_public,
                'private':self.keys_private,
                'secret':self.keys_secret
            }}
    