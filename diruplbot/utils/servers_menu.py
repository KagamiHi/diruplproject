from discord import SelectOption, Interaction
from discord.ui import View, Select

from rustplus.exceptions import RequestError, ClientNotConnectedError

from rustsocket import CustomRustSocket
from dirupl.address_directory.models import Guildinfo, Server


class ServersMenu(Select):
    def __init__(self, rust_sockets, servers):
        self.rust_sockets = rust_sockets
        options = [
            SelectOption(label=server.name, value=server.id.hex) for server in servers
        ]

        super().__init__(placeholder='Choose a Server!', 
                         min_values=1, 
                         max_values=1, 
                         options=options
                        )

    async def callback(self, interaction: Interaction): # the function called when the user is done selecting options
        server = await Server.objects.filter(id=self.values[0]).afirst()
        if server is None:
            self.placeholder = "Unknown server"
        else:
            self.placeholder = server.name
        self.disabled = True
        await interaction.response.edit_message(view=self.view)

        if server is None:
            return
        
        guild_id = interaction.guild_id
        if guild_id in self.rust_sockets:
            await self.rust_sockets[guild_id].break_socket()

        guildinfo = await self.save_new_server(guild_id, server)
        
        rustsocket = CustomRustSocket(guildinfo, interaction.channel)
        try:
            await rustsocket.start()
        except (RequestError, ClientNotConnectedError) as e:
            await guildinfo.server.adelete()
            guildinfo.server = None
            await guildinfo.asave()
            await interaction.channel.send('Server is broken')
        except ConnectionAbortedError:
            await interaction.channel.send('Server is not available')
            return
            
        self.rust_sockets[guild_id] = rustsocket
        

    async def save_new_server(self, guild_id, server):
        guildinfo = await Guildinfo.objects.select_related('notification_settings').aget(_guild_id=guild_id)
        
        if guildinfo is None:
            return

        guildinfo.server = server
        await guildinfo.asave()
        return guildinfo



class ServersMenuView(View):

    def __init__(self, rust_sockets, servers):
        super().__init__(timeout=None)
        self.add_item(ServersMenu(rust_sockets, servers))
