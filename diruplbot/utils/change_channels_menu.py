from discord import SelectOption, Interaction
from discord.ui import View, Select


class ChangeChannelsMenu(Select):
    def __init__(self,guildinfo, channels):
        self.guildinfo = guildinfo
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
        self.guildinfo.channel_id = self.values[0]
        return await self.guildinfo.asave()
        



class ChangeChannelsMenuView(View):

    def __init__(self, guildinfo, channels):
        super().__init__(timeout=60)
        self.add_item(ChangeChannelsMenu(guildinfo, channels))