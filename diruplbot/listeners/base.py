from discord.ext import commands
from discord import BotIntegration

from diruplbot.utils import Guild

import logging

log = logging.getLogger("DiruplBot")

class BaseListenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        integrations = await guild.integrations()
        for integration in integrations:
            if isinstance(integration, BotIntegration):
                if integration.application.user.name == self.bot.user.name:
                    bot_inviter = integration.user # returns a discord.User object
                    
                    new_guild = Guild(bot_inviter, guild)
                    await new_guild.register()
                    return
                