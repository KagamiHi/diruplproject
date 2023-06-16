from .channels_menu import ChannelsMenuView
from discord import TextChannel

from dirupl.address_directory.models import Guildinfo, NotificationSettings
from dirupl.users.models import CustomUser


class Guild():
    def __init__(self, bot, inviter, guild):
        self.bot = bot
        self.inviter = inviter
        self.guild = guild
        self.channel = None
        self.channels = None
        self.members = None

    async def is_valid(self):
        if self.inviter:
            return True
        return False
    
    async def send_select_channel(self):
        try:
            await self.inviter.send(f"{self.inviter.display_name}, hi!", view = ChannelsMenuView(self, await self.collect_channels()))
        except NoChannelsError:
            await self.inviter.send(f"{self.inviter.display_name}, hi!\n I don't see chats that I can write to")

    async def collect_channels(self):
        all_channels = self.guild.channels
        allowed_channels = []

        for channel in all_channels:
            if isinstance(channel, TextChannel):
                if [m.name for m in channel.members if m.bot and m.id == self.bot.user.id]:
                    allowed_channels.append(channel)
        if allowed_channels:
            self.channels = allowed_channels
            return allowed_channels
        raise NoChannelsError

    async def take_channel(self, channel_name):
        for channel in self.channels:
            if channel.name == channel_name:
                self.channel = channel
                return channel
            
    async def create_guild_model(self):
        if self.channel is None:
            return

        guild_model = await Guildinfo.objects.filter(_guild_id=self.guild.id).afirst()
        if guild_model:
            return
        
        notification_settings = await NotificationSettings.objects.acreate()
        guild_model = await Guildinfo.objects.acreate(
            _guild_id=self.guild.id,
            name = self.guild.name,
            inviter_id=self.inviter.id, 
            channel_id=self.channel.id,
            notification_settings=notification_settings,
            )
        
        for member in self.channel.members:
            user = await CustomUser.objects.filter(discord_user_id=member.id).afirst()
            if user:
                await guild_model.members.aadd(user)

        await guild_model.asave()
        self.guild_model = guild_model
        return guild_model


class GuildException(Exception):
    pass

class NoChannelsError(GuildException):
    pass