from discord.ext import commands
from discord import BotIntegration

from diruplbot.utils import Guild
from dirupl.address_directory.models import Guildinfo

from rustsocket import CustomRustSocket


class BaseListenerCog(commands.Cog):
    def __init__(self, bot, rust_sockets):
        self.bot = bot
        self.rust_sockets = rust_sockets

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        integrations = await guild.integrations()
        for integration in integrations:
            if isinstance(integration, BotIntegration):
                if integration.application.user.name == self.bot.user.name:
                    bot_inviter = integration.user # returns a discord.User object
                    
                    new_guild = Guild(bot_inviter, guild)
                    await new_guild.send_select_channel()
                    return new_guild # returns a diruplbot.utils.Guild object
                
    @commands.Cog.listener()
    async def on_ready(self):
        ### Takes guild info from the selected server and start rust_socket on it ###
        async for gi in Guildinfo.objects.select_related('server', 'notification_settings').filter(server__isnull=False).all():
            channel = await self.bot.fetch_channel(gi.channel_id)
            rustsocket = CustomRustSocket(gi, channel)
            self.rust_sockets[gi.guild_id] = rustsocket # add socket to the dict
            await rustsocket.start()
            
                