import asyncio
from re import match
from rustplus import RustSocket
from rustplus.exceptions import RequestError
from rustplus import ChatEvent

from rustplus.api.remote.rustplus_proto import AppEmpty

from .message import MessageVendingInfo, MessageEventsInfo


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
        return True

    async def break_socket(self):
        if hasattr(self, 'time_future'):
            self.time_future.cancel()
        if hasattr(self, 'socket'):
            await self.socket.disconnect()

    async def user_connect(self):
        self.socket = RustSocket(self.server.ip, self.server.port, self.server.playerid, self.server.playertoken)

        try:
            await self.socket.connect(retries=5)
            server_info = await self.socket.get_info()
        except (RequestError, ConnectionAbortedError):
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

    async def change_channel(self, new_channel):
        self.channel = new_channel
        self.model.channel_id = new_channel.id
        await self.model.asave()
        return self.model.channel_id

################ Regular functions ###################

    async def get_server_time(self):
        time_on_server = await self.socket.get_time()
        server_time = time_on_server.time
        await self.send_message(f'Server time: {server_time}')

    async def get_server_info(self):
        server_info = await self.socket.get_info()
        await self.channel.send(f"{server_info.name} {server_info.players}/{server_info.max_players}\n In queue: {server_info.queued_players}")

    async def get_vending_machines(self, item_name, steam_id = None):
        events = await self.custom_get_markers()
        
        info = MessageVendingInfo(events, worldsize = self.size,show_location=self.settings.vend_show_location, show_distance=self.settings.vend_show_distance)
        
        if self.settings.vend_show_distance:
            if not steam_id:
                steam_id = self.server._playerid
            team_info = await self.socket.get_team_info()
            info.member_x, info.member_y = await self.get_member_coodinates(team_info.members, steam_id)
        
        message = await info.data_processing(item_name)
        if message:
            await self.channel.send(message)
        else:
            await self.channel.send('No vending machines')
        
    async def get_server_events(self, steam_id = None):
        events = await self.socket.get_current_events()

        if not events:
            await self.send_message('No events on server.')
            return
        
        info = MessageEventsInfo(events, worldsize = self.size, show_location=self.settings.event_show_location, show_distance=self.settings.event_show_distance)

        if self.settings.event_show_distance:
            if not steam_id:
                steam_id = self.server._playerid
            team_info = await self.socket.get_team_info()
            info.member_x, info.member_y = await self.get_member_coodinates(team_info.members, steam_id)
        message = await info.data_processing()

        
        await self.send_message(message)
        
                
################ Messages parts ##################

    async def send_message(self, text):
        await self.socket.send_team_message(text)

    async def message_receiver(self):
        async def chat(event : ChatEvent):
            message = event.message
            if message.message.startswith('!'):
                await self.get_discord_command(message)
                return

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
            await self.get_vending_machines(command_name.split(' ')[1], event.steam_id)
        elif command_name in ['events']:
            await self.get_server_events(event.steam_id)

############## Settings #########################

    async def change_event_location_status(self):
        self.settings.event_show_location = not self.settings.event_show_location
        await self.settings.asave()
        if self.settings.event_show_location:
            status = 'visible'
        else:
            status = 'hidden'
        await self.channel.send(f'Event locations {status}')

    async def change_event_distance_status(self):
        self.settings.event_show_distance = not self.settings.event_show_distance
        await self.settings.asave()
        if self.settings.event_show_distance:
            status = 'visible'
        else:
            status = 'hidden'
        await self.channel.send(f'Events distances {status}')

    async def change_vend_location_status(self):
        self.settings.vend_show_location = not self.settings.vend_show_location
        await self.settings.asave()
        if self.settings.event_show_distance:
            status = 'visible'
        else:
            status = 'hidden'
        await self.channel.send(f'Vending machines locations {status}')

    async def change_vend_distance_status(self):
        self.settings.vend_show_distance = not self.settings.vend_show_distance
        await self.settings.asave()
        if self.settings.event_show_distance:
            status = 'visible'
        else:
            status = 'hidden'
        await self.channel.send(f'Vending machines distances {status}')


############## Others ###########################

    async def custom_get_markers(self):

        await self.socket._handle_ratelimit()

        app_request = self.socket._generate_protobuf()
        app_request.get_map_markers = AppEmpty()
        app_request.get_map_markers._serialized_on_wire = True

        await self.socket.remote.send_message(app_request)

        app_message = await self.socket.remote.get_response(app_request.seq, app_request)
        return app_message.response.map_markers.markers

    async def get_member_coodinates(self, members, steam_id):
        for m in members:
                if m.steam_id == steam_id and m.is_alive:
                    return m.x, m.y
        return None, None




class RustSocketException(Exception):
    pass

class PlayerIdTokenError(RustSocket):
    pass