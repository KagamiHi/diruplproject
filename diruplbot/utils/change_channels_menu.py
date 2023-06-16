from discord import SelectOption, Interaction
from discord.ui import View, Select

from . import NoChannelsError
from discord import TextChannel

class ChangeChannelsMenu(Select):
    def __init__(self,rustsocket, channels):
        self.rustsocket = rustsocket
        self.channels = channels
        options = [
            SelectOption(label=channel.name, value=channel.id) for channel in channels
        ]

        super().__init__(placeholder='Choose a Channel!', 
                         min_values=1, 
                         max_values=1, 
                         options=options
                        )

    async def callback(self, interaction: Interaction): # the function called when the user is done selecting options
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        channel = await self.take_channel()
        if not channel:
            return
        await self.rustsocket.change_channel(channel)
        return self.values[0]
        
    async def take_channel(self):
        for channel in self.channels:
            if channel.id == int(self.values[0]):
                return channel


class ChangeChannelsMenuView(View):

    def __init__(self, rustsocket, channels):
        super().__init__(timeout=60)
        self.add_item(ChangeChannelsMenu(rustsocket, channels))


async def collect_channels(bot, all_channels):
    allowed_channels = []
    for channel in all_channels:
        if isinstance(channel, TextChannel):
            if [m.name for m in channel.members if m.bot and m.id == bot.user.id]:
                allowed_channels.append(channel)
                
    if allowed_channels:
        return allowed_channels
    raise NoChannelsError