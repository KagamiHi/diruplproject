from discord import SelectOption, Interaction
from discord.ui import View, Select



class ChannelsMenu(Select):
    def __init__(self, channels, new_guild):
        self.new_guild = new_guild
        options = [
            SelectOption(label=channel.name) for channel in channels
        ]

        super().__init__(placeholder='Choose a Channel!', 
                         min_values=1, 
                         max_values=1, 
                         options=options
                        )

    async def callback(self, interaction: Interaction): # the function called when the user is done selecting options
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        await self.new_guild.take_channel(self.values[0])
        new_model = await self.new_guild.create_guild_model()
        return new_model
        



class ChannelsMenuView(View):

    def __init__(self, new_guild, channels):
        super().__init__(timeout=None)
        self.add_item(ChannelsMenu(channels, new_guild))
