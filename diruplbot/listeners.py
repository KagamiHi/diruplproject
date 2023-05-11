from discord.ext import commands
from discord.channel import DMChannel

from django.db import transaction
from asgiref.sync import sync_to_async
from django.contrib.auth.forms import SetPasswordForm

from dirupl.users.models import CustomUser
from dirupl.users.forms import CustomUserCreationForm
from dirupl.address_directory.models import Credential

class DirectListenerCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief= 'Send to Direct `!registr <login> <password>` to registr.', description='The start of player registration')
    async def register(self, ctx, login, password):

        if isinstance(ctx.channel, DMChannel):
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
        Credential.objects.create(user=user)
        return 'You are registred\nLog in to your account to link the bot to Steam.\n {URL}'
    
    @commands.command(brief= 'Send to Direct `!reset_password <new password>` to change password.', description='Forgot your password?')
    async def reset_password(self, ctx, password):

        if isinstance(ctx.channel, DMChannel):
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