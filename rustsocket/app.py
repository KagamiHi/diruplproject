import asyncio
from re import match
from rustplus import RustSocket
from rustplus.exceptions import RequestError
from rustplus import ChatEvent

from rustplus.api.remote.rustplus_proto import AppEmpty

from .message import MessageVendingInfo, MessageEventsInfo
from .utils import Server_timer


class CustomRustSocket():
    def __init__(self, model, channel):
        self.model=model
        self.server=model.server
        self.settings=model.notification_settings
        self.channel = channel
        
    
    async def start(self):
        if not await self.user_connect():
            return
        await self.get_team_chat()
        if self.settings.check_time:
            self.time_future = asyncio.ensure_future(self.check_time_loop())
        return True

    async def break_socket(self):
        if hasattr(self, 'time_future'):
            self.time_future.cancel()
        if hasattr(self, 'socket'):
            await self.socket.disconnect()

    async def user_connect(self):
        self.socket = RustSocket(self.server.ip, self.server.port, self.server.playerid, self.server.playertoken)

        await self.socket.connect()
        try:
            server_info = await self.socket.get_info()
        except RequestError:
            return
        self.size = server_info.size
        await self.message_receiver()
        return True
    
    async def check_team_info(self):
        team_info = await self.socket.get_team_info()
        print (team_info)

    async def get_team_chat(self):
        try:
            messages = await self.socket.get_team_chat()
        except RequestError:
            await self.channel.send('Please, create a team on server.')
            return
        
        if self.settings.last_message_time == 1:
            for message in messages:
                if not message.message.startswith('!'):
                    list_msg = await self.channel.send(f"{message.name}: {message.message}")
                    if not list_msg:
                        return
                    self.settings.last_message_time = message.time
            await self.settings.asave()
            return
        
        last_message_time = self.settings.last_message_time
        for message in messages:
            if message.time > last_message_time:
                list_msg = await self.channel.send(f"{message.name}: {message.message}")
                if not list_msg:
                    return
                self.settings.last_message_time = message.time
        await self.settings.asave()


################ Regular functions ###################
    async def server_time_loop(self):
        def str_time_to_int(string):
            time_parts = string.split(':')
            time_in_minutes = int(time_parts[0])*60+int(time_parts[1])
            return time_in_minutes
        
        rust_time = await self.socket.get_time()
        act_time = str_time_to_int(rust_time.time)
        res_time = act_time + 30
        await asyncio.sleep(150)
        rust_time = await self.socket.get_time()
        act_time = str_time_to_int(rust_time.time)
        if res_time == act_time:
            print (True)
        else:
            print (res_time-act_time)


    async def check_time_loop(self):
        timer = Server_timer(self.socket, self.send_message)
        

    async def check_server_time(self):
        time_on_server = await self.socket.get_time()
        server_time = time_on_server.time
        await self.send_message(f'Server time: {server_time}')

    async def change_time_status(self):
        if self.settings.check_time:
            self.time_future.cancel()
            self.settings.check_time = False
        else:
            self.settings.check_time = True
            self.time_future = asyncio.ensure_future(self.check_time_loop())
        await self.settings.asave()

    async def get_server_info(self):
        server_info = await self.socket.get_info()
        await self.channel.send(f"{server_info.name} {server_info.players}/{server_info.max_players}\n In queue: {server_info.queued_players}")

    async def get_vending_machines(self, item_name):
        events = await self.custom_get_markers()
        if not events:
            return
        info = MessageVendingInfo(events, self.size)
        message = await info.data_processing(item_name)
        if message:
            await self.channel.send(message)
        else:
            await self.channel.send('No vending machines')
        
    async def get_server_events(self, steam_id = None):
        events = await self.socket.get_current_events()
        # if not events:
        #     await self.send_message('No events on server.')
        #     return
        
        info = MessageEventsInfo(events, self.size, steam_id)
        team_info = await self.socket.get_team_info()
        message = await info.data_processing_with_distance(team_info.members)
        if message:
            await self.send_message(message)
        
                
################ Messages parts ##################

    async def send_message(self, text):
        await self.socket.send_team_message(text)

    async def message_receiver(self):
        async def chat(event : ChatEvent):
            message = event.message
            if message.message.startswith('!'):
                await self.get_discord_command(message)

            member_list = [member.name for member in self.channel.members]
            if message.message.split(':')[0] in member_list:
                list_msg = await self.channel.send(f"{message.message}")
            else:
                list_msg = await self.channel.send(f"{message.name}: {message.message}")
            if not list_msg:
                return
            self.settings.last_message_time = message.time
            await self.settings.asave()

        self.socket.chat_event(chat)

    async def get_discord_command(self, event):
        command_name = event.message[1:].lower()
        if command_name in ['server', 'si', 'server_info', 'pop']:
            await self.get_server_info()
        elif command_name in ['show_time', 'st']:
            await self.check_server_time()
        elif match(r'shop [a-zA-Z]{1,20}', command_name):
            await self.get_vending_machines(command_name.split(' ')[1])
        elif command_name in ['events', ' events']:
            await self.get_server_events(event.steam_id)

############## Others ###########################

    async def custom_get_markers(self):

        await self.socket._handle_ratelimit()

        app_request = self.socket._generate_protobuf()
        app_request.get_map_markers = AppEmpty()
        app_request.get_map_markers._serialized_on_wire = True

        await self.socket.remote.send_message(app_request)

        app_message = await self.socket.remote.get_response(app_request.seq, app_request)
        return app_message.response.map_markers.markers



class RustSocketException(Exception):
    pass

class PlayerIdTokenError(RustSocket):
    pass