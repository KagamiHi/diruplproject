from discord.ext import commands
from discord.channel import DMChannel

from django.db import transaction
from asgiref.sync import sync_to_async
from django.contrib.auth.forms import SetPasswordForm
from django.forms.utils import ErrorDict

from dirupl.users.models import CustomUser
from dirupl.users.forms import CustomUserCreationForm
from dirupl.address_directory.models import Credential, Guildinfo

from uuid import uuid4
from push_receiver.register import register

from diruplbot.utils import Link_app
import logging

log = logging.getLogger("DiruplBot")


class DirectListenerCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief= 'Registration', description='The start of player registration.')
    async def register(self, ctx, login, password):

        if isinstance(ctx.channel, DMChannel):
            async with ctx.channel.typing():
                answer = await self.register_user(ctx.author.id, login, password)
                await ctx.channel.send (answer)
        else:
            await ctx.channel.send ('You can register in Direct')

    async def register_user(self, discord_user_id, login, password):
        
        user = await self.create_user(login, discord_user_id, password)
        if isinstance(user, ErrorDict):
            error_dict = user.as_data()
            error = str(error_dict[list(error_dict)[0]][0]).replace("['", "").replace("']", "")
            return error
        
        discord_user = await self.bot.fetch_user(discord_user_id)
        common_guilds = discord_user.mutual_guilds
        for guild in common_guilds:
            gi = await Guildinfo.objects.aget(_guild_id=guild.id)
            await gi.members.aadd(user)
            await gi.asave()

        """
        Create credential for user.
        """
        try:
            await Credential.objects.acreate(user=user)
        except KeyError as e:
            log.debug(f"Keyerror: {e}")
            return 'Registration is not available at the moment'
        return 'You are registred\Send `!link_steam <steam login> <steam password>` to link the bot to Steam.\n {URL}'

    @sync_to_async
    @transaction.atomic
    def create_user(self, login, discord_user_id, password):
        user_creation_form = CustomUserCreationForm(data={'login':login,'discord_user_id':discord_user_id, 'password1':password, 'password2':password})
        
        if not user_creation_form.is_valid():
            return user_creation_form.errors
        
        user = user_creation_form.save()

        return user

    @commands.command(brief= 'Change password', description='Forgot your password?')
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
    
    
    @commands.command(brief= 'Link steam and rust for new Rust+ app', description='The second step of the registration.')
    async def link_steam(self, ctx, login, password):

        if not isinstance(ctx.channel, DMChannel):
            await ctx.channel.send ('You can link steam in Direct')

        async with ctx.channel.typing():
            la = Link_app(self.bot, ctx, login, password)
            await la.link()

    
    @commands.command(brief= 'Create new credentials')
    async def new_credentials(self, ctx):
        
        if not isinstance(ctx.channel, DMChannel):
            await ctx.channel.send ('You can link steam in Direct')

        async with ctx.channel.typing():
            await self.change_credential(ctx.author.id)

        return
    
    @sync_to_async
    @transaction.atomic
    def change_credential(self, user_id):
        
        user = CustomUser.objects.filter(discord_user_id=user_id).first()
        credential = Credential.objects.filter(user=user).first()
        
        sender_id = 976529667804
        appId = "wp:receiver.push.com#{}".format(uuid4())
        credential_dict = register(sender_id=sender_id, app_id=appId)

        credential.keys_private = credential_dict['keys']['private']
        credential.keys_public = credential_dict['keys']['public']
        credential.keys_secret = credential_dict['keys']['secret']
        credential.fcm_token = credential_dict['fcm']['token']
        credential.fcm_pushset = credential_dict['fcm']['pushSet']
        credential.gcm_token = credential_dict['gcm']['token']
        credential.gcm_androidid = credential_dict['gcm']['androidId']
        credential.gcm_securitytoken = credential_dict['gcm']['securityToken']
        credential.gcm_appid = credential_dict['gcm']['appId']
        credential.rust_registration_status = False
        credential.save()