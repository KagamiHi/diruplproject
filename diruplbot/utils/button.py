from discord.ui import View, button
from discord import ButtonStyle
from dirupl.address_directory.models import Server

# from rustsocket.app import 


class ServerButtonChooseView(View):
    def __init__(self, server_id):
        super().__init__(timeout=None)
        self.server_id = server_id

    @button(label="Choose", row=0, style=ButtonStyle.blurple)
    async def choose_server(self, int, button):
        await int.response.edit_message(view=ServerButtonDeclineView(self.server_id))
        server = await Server.objects.filter(id=self.server_id).afirst()
        if server is None:
            return
        server.stream = True
        await server.asave()
        


class ServerButtonDeclineView(View):
    def __init__(self, server_id):
        super().__init__(timeout=None)
        self.server_id = server_id

    @button(label="Decline", row=0, style=ButtonStyle.red)
    async def choose_server(self, int, button):
        await int.response.edit_message(view=ServerButtonChooseView(self.server_id))
        server = await Server.objects.filter(id=self.server_id).afirst()
        if server is None:
            return
        server.stream = False
        await server.asave()
        

        
