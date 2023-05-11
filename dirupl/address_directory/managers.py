from django.db import models

from uuid import uuid4
from push_receiver.register import register

class CredentialManager(models.Manager):
    def create(self, user):
        sender_id = 976529667804
        appId = "wp:receiver.push.com#{}".format(uuid4())
        credential_dict = register(sender_id=sender_id, app_id=appId)
        credential = self.model(
            user=user,
            keys_private = credential_dict['keys']['private'],
            keys_public = credential_dict['keys']['public'],
            keys_secret = credential_dict['keys']['secret'],
            fcm_token = credential_dict['fcm']['token'],
            fcm_pushset = credential_dict['fcm']['pushSet'],
            gcm_token = credential_dict['gcm']['token'],
            gcm_androidid = credential_dict['gcm']['androidId'],
            gcm_securitytoken = credential_dict['gcm']['securityToken'],
            gcm_appid = credential_dict['gcm']['appId'],
        )
        credential.save()
        return credential