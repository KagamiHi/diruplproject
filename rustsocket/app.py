import asyncio
from rustplus import RustSocket

# from dirupl.address_directory.models import Server

class CustomRustSocket():
    def __init__(self, ctx):
        self.ctx=ctx
    
    async def user_connect(self, server_id):
        # server = await Server.objects.filter(id=server_id).afirst()
        # try:
        #     playerId, playerToken = int(server.playerid), int(server.playertoken)
        # except ValueError:
        #     raise PlayerIdTokenError

        # socket = RustSocket(server.ip, server.port, playerId, playerToken)

        self.socket = RustSocket('45.88.230.81', '28083', 76561198042626541, -644358222)
        await self.socket.connect()
        
    
    async def break_socket(self):
        await self.socket.disconnect()

    
    async def check_team_info(self):
        team_info = await self.socket.get_team_info()
        print (team_info)


    async def get_team_chat(self):
        await self.socket.get_team_chat()

async def main():
    s = CustomRustSocket('bob')
    await s.user_connect(123)
    await s.check_team_info()
    await s.break_socket()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Caught keyboard interrupt. Canceling tasks...")


class RustSocketException(Exception):
    pass

class PlayerIdTokenError(RustSocket):
    pass