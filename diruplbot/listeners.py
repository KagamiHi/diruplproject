from discord.ext import commands
from discord.channel import DMChannel

from django.db import transaction
from asgiref.sync import sync_to_async

from dirupl.users.models import CustomUser


class DirectListenerCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief= 'Send to Direct `!registr <login> <password>` to registr.', description='The start of player registration')
    async def register(self, ctx, login, password):
        if isinstance(ctx.channel, DMChannel):
            await self.register_user(ctx.author.id, login, password)
            await ctx.channel.send (f'You are registred as {login}')
            
        else:
            await ctx.channel.send ('You can register in Direct')

    @sync_to_async
    @transaction.atomic
    def register_user(self, discord_user_id, login, password):
        # User.objects.create(login=login, password=password, discord_user_id=discord_user_id)
        print (discord_user_id)
        # print (CustomUser.objects.first())