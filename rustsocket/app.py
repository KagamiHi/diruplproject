import asyncio
from asgiref.sync import sync_to_async
from rustplus import RustSocket

# from dirupl.address_directory.models import Server

class CustomRustSocket():
    def __init__(self, model, channel):
        self.model=model
        self.server=model.server
        self.settings=model.notification_settings
        self.channel = channel
    

    async def user_connect(self):
        try:
            playerId, playerToken = self.server.playerid, self.server.playertoken
        except ValueError:
            raise PlayerIdTokenError

        self.socket = RustSocket(self.server.ip, self.server.port, playerId, playerToken)

        await self.socket.connect()
        
    
    async def break_socket(self):
        if self.time_future:
            self.time_future.cancel()
        if self.socket:
            await self.socket.disconnect()

    
    async def check_team_info(self):
        team_info = await self.socket.get_team_info()
        print (team_info)


    async def get_team_chat(self):
        team_info = await self.socket.get_team_info()
        if team_info is None:
            await self.channel.send('Create team')
            return 
        
        # await self.socket.get_team_chat()

    async def start(self):
        await self.user_connect()
        await self.get_team_chat()
        if self.settings.check_time:
            self.time_future = asyncio.ensure_future(self.check_time_loop())
        pass

    async def check_time_loop(self):
        while True:
            time_on_server = await self.socket.get_time()
            await self.channel.send(time_on_server.time)
            await asyncio.sleep(5)

    async def check_server_time(self):
        time_on_server = await self.socket.get_time()
        await self.channel.send(time_on_server.time)

    async def change_time_status(self):
        if self.settings.check_time:
            self.time_future.cancel()
            self.settings.check_time = False
        else:
            self.settings.check_time = True
            self.time_future = asyncio.ensure_future(self.check_time_loop())
        await self.settings.asave()


    async def take_server_info(self):
        server_info = await self.socket.get_info()
        await self.channel.send(f"{server_info.name} {server_info.players}/{server_info.max_players}\n In queue: {server_info.queued_players}")


class RustSocketException(Exception):
    pass

class PlayerIdTokenError(RustSocket):
    pass