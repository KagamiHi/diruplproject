from discord.ext import commands
from diruplbot.listeners import DirectListenerCog
from discord.channel import DMChannel
from discord import Message


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
