from discord.ext import commands
from discord import BotIntegration

from rustplus.exceptions import RequestError

from diruplbot.utils import Guild
from dirupl.address_directory.models import Guildinfo
from dirupl.users.models import CustomUser

from rustsocket import CustomRustSocket



class BaseListenerCog(commands.Cog):
    def __init__(self, bot, rust_sockets):
        self.bot = bot
        self.rust_sockets = rust_sockets

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        ### When the bot joins a guild, creates Guild to build Guildinfo in datebase ###
        integrations = await guild.integrations()
        for integration in integrations:
            if isinstance(integration, BotIntegration): 
                if integration.application.user.name == self.bot.user.name: # finds this bot
                    bot_inviter = integration.user # returns a discord.User object
                    
                    new_guild = Guild(self.bot, bot_inviter, guild)
                    await new_guild.send_select_channel() # send select menu to setup Dirupl channel
                    return new_guild # returns a diruplbot.utils.Guild object

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if not before.guild.id in self.rust_sockets:
            return
        
        rust_socket = self.rust_sockets[before.guild.id]
        
        if before.id !=rust_socket.channel.id:
            return
        
        if len(before.members) == len(after.members):
            return
        elif len(before.members) > len(after.members): # member go away
            for member in before.members:
                if member.bot:
                    continue

                if member in after.members:
                    continue
                
                await self.remove_member_from_guildinfo(member.id, rust_socket.member)
        else:                                          # new member
            for member in after.members:
                if member.bot:
                    continue

                if member in before.members:
                    continue

                await self.add_member_to_guildinfo(member.id, rust_socket.model)


    @commands.Cog.listener()
    async def on_ready(self):
        ### Takes guild info from the selected server and start rust_socket on it ###
        async for gi in Guildinfo.objects.select_related('server', 'notification_settings').prefetch_related('members').filter(server__isnull=False).all():
            channel = await self.bot.fetch_channel(gi.channel_id)
            
            for member in channel.members:
                if member.bot:
                    continue
                await self.add_member_to_guildinfo(member.id, gi)

            rustsocket = CustomRustSocket(gi, channel)
            try:
                await rustsocket.start()
            except RequestError:
                await channel.send('Server is broken')
                await gi.server.adelete()
                gi.server = None
                await gi.asave()
                continue
            except ConnectionAbortedError:
                await channel.send('Server is not available')
                continue
            self.rust_sockets[gi.guild_id] = rustsocket # add socket to the dict


    async def add_member_to_guildinfo(self, user_id, guildinfo):
        user = await CustomUser.objects.filter(discord_user_id=user_id).afirst()
        if not user:
            return
        
        if user in guildinfo.members.all():
            return
        
        await guildinfo.members.aadd(user)
        await guildinfo.asave()
        return guildinfo
    
    async def remove_member_from_guildinfo(self, user_id, guildinfo):
        user = await CustomUser.objects.filter(discord_user_id=user_id).afirst()
        if not user:
            return
        
        if not user in guildinfo.members.all():
            return
        
        await guildinfo.members.aremove(user)
        await guildinfo.asave()
        return guildinfo