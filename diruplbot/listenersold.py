from discord.ext import commands
from discord.channel import DMChannel
from discord import client

from django.db import transaction
from asgiref.sync import sync_to_async
from django.contrib.auth.forms import SetPasswordForm

from dirupl.users.models import CustomUser
from dirupl.users.forms import CustomUserCreationForm
from dirupl.address_directory.models import Credential
from dirupl.address_directory.utils import Server_info_catcher, UserRegError, RustRegStatusError


from diruplbot.utils import Link_app, server_to_msg

from rustsocket.app import CustomRustSocket, PlayerIdTokenError

import logging

log = logging.getLogger("DiruplBot")


class BaseListenerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Bot.event
    async def on_guild_join(self, guild):
        print ('joined')

class DirectListenerCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief= 'Send to Direct `!registr <login> <password>` to registr.', description='The start of player registration.')
    async def register(self, ctx, login, password):

        if isinstance(ctx.channel, DMChannel):
            async with ctx.channel.typing():
                answer = await self.register_user(ctx.author.id, login, password)
                await ctx.channel.send (answer)
        else:
            await ctx.channel.send ('You can register in Direct')

    @sync_to_async
    @transaction.atomic
    def register_user(self, discord_user_id, login, password):
        
        user_creation_form = CustomUserCreationForm(data={'login':login,'discord_user_id':discord_user_id, 'password1':password, 'password2':password})
        
        if not user_creation_form.is_valid():
            return user_creation_form.errors
        
        user = user_creation_form.save()
        """
        Create credential for user.
        """
        try:
            Credential.objects.create(user=user)
        except KeyError as e:
            log.debug(f"Keyerror: {e}")
            return 'Registration is not available at the moment'
        return 'You are registred\Send `!link_steam <steam login> <steam password>` to link the bot to Steam.\n {URL}'
    
    @commands.command(brief= 'Send to Direct `!reset_password <new password>` to change password.', description='Forgot your password?')
    async def reset_password(self, ctx, password):

        if isinstance(ctx.channel, DMChannel):
            async with ctx.channel.typing():
                answer = await self.change_user_password(ctx.author.id, password)
                await ctx.channel.send (answer)  
        else:
            await ctx.channel.send ('You can register in Direct')

    @sync_to_async
    @transaction.atomic
    def change_user_password(self, discord_user_id, password):

        user = CustomUser.objects.filter(discord_user_id=discord_user_id).first()

        if user is None:
            return f'You are not registred'
        
        if len(password)<8:
            return f'Your password must contain at least 8 characters'
        
        set_password_form = SetPasswordForm(user=user, data={'new_password1':password, 'new_password2':password})
        
        if not set_password_form.is_valid():
            return set_password_form.errors
        
        set_password_form.save()
        return 'Your password has been changed'
    
    @commands.command(brief= 'Send to Direct `!link_steam <steam login> <steam password>` to link steam and rust for new Rust+ app.', description='The second step of the registration.')
    async def link_steam(self, ctx, login, password):

        if not isinstance(ctx.channel, DMChannel):
            await ctx.channel.send ('You can link steam in Direct')

        async with ctx.channel.typing():
            la = Link_app(self.bot, ctx, login, password)
            await la.link()

class SettingsListenerCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['LFS', 'lfs'], brief= 'Send to Direct `!LFS` to search server.', description='Looking for server command.')
    async def looking_for_server(self, ctx):

        if isinstance(ctx.channel, DMChannel):
            async with ctx.channel.typing():
                sic = Server_info_catcher(ctx.author.id)
                try:
                    await sic.check_health()
                except (UserRegError, RustRegStatusError) as exp:
                    if isinstance(exp, UserRegError):
                        await ctx.channel.send ("You are not registered")
                    else:
                        await ctx.channel.send ("You are not linked")
                    return
                term = 30
                await ctx.channel.send (f"Searching...({term} sec)")
                await sic.catch_info(term)
                await server_to_msg(ctx)   
        else:
            await ctx.channel.send ('You can search in Direct')

    @commands.command(aliases=['show', 'shows'], brief= 'Send to Direct `!show` to show your servers.')
    async def show_server(self, ctx):
        if isinstance(ctx.channel, DMChannel):
            await server_to_msg(ctx)
        else:
            await ctx.channel.send ('You can show in Direct')

    @commands.command(aliases=['stream'], brief= '`!stream` to receive messages from server.')
    async def start_stream(self, ctx):
        return
        try:
            await CustomRustSocket.user_connect(server_id)
        except PlayerIdTokenError:
            await ctx.channel.send ('Contact admin')

