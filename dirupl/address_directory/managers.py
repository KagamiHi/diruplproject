from django.db import models

from uuid import uuid4
from push_receiver.register import register


import logging

log = logging.getLogger("Manager")

class CredentialManager(models.Manager):
    def create(self, user):
        sender_id = 976529667804
        appId = "wp:receiver.push.com#{}".format(uuid4())
        credential_dict = register(sender_id=sender_id, app_id=appId)
        try:
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
        except KeyError as e:
            log.debug(f'{e}')
            return
        return credential
    

class ServerManager(models.Manager):
    def create_from_dict(self, user, dict):
        desc = dict['desc'].split()
        try:
            server = self.model(
                user = user,
                server_id = dict['id'],
                name = dict['name'],
                desc = desc,
                url = dict['url'],
                img = dict['img'],
                logo = dict['logo'],
                ip = dict['ip'],
                _playerid = dict['playerId'],
                _playertoken = dict['playerToken'],
                port = dict['port'],
            )
            server.save()
        except KeyError as e:
            log.debug(f'{e}')
            return
        return server

class GuildinfoManager(models.Manager):
    async def acreate(self, guild_id, inviter_id, channel_id, notification_settings):
        try:
            guildinfo = self.model(
                guild_id = guild_id, 
                inviter_id = inviter_id,
                channel_id = channel_id, 
                notification_settings = notification_settings,
            )
            await guildinfo.asave()
        except KeyError as e:
            log.debug(f'{e}')
            return
        return guildinfo
