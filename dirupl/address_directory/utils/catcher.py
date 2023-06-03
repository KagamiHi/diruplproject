from json import loads
import logging
import asyncio

from dirupl.address_directory.utils import PushReceiver

from dirupl.users.models import CustomUser
from dirupl.address_directory.models import Credential, Server


log = logging.getLogger("push_receiver")

class Server_info_catcher():
  
  def __init__(self, discord_user_id):
    self.discord_user_id = discord_user_id

  async def check_health(self):

    user = await CustomUser.objects.filter(discord_user_id=self.discord_user_id).afirst()
    
    if user is None:
      log.debug(f"User is not registred")
      raise UserRegError
    
    credentials = await Credential.objects.filter(user=user).afirst()

    if credentials is None:
      log.debug(f"User's credentials is not created")
      raise UserRegError
    
    if credentials.rust_registration_status == False:
      raise RustRegStatusError
    
    self.user = user
    self.credentials = credentials
    return credentials

  async def catch_info(self, term):
    
    fcm_credentials= await self.credentials.fcm_credentials_to_dict()

    catcher = PushReceiver(fcm_credentials)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, catcher.listen, self.on_notification, term)

  def on_notification(self, obj, notification, data_message):
    server_dict = loads(notification['data']['body'])
    
    if server_dict['type'] != 'server':
      return
    
    this_server = Server.objects.filter(user=self.user, ip = server_dict['ip']).first()
    if this_server is not None:
      if server_dict['playerToken'] == this_server._playertoken:
        return
      this_server.delete()
    server_info = Server.objects.create_from_dict(self.user, server_dict)
    if server_info is None:
      log.debug(f"Server is not created")


class ServerCatcherException(Exception):
  pass

class UserRegError(ServerCatcherException):
  pass

class RustRegStatusError(ServerCatcherException):
  pass
