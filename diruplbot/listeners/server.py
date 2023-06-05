from discord.ext import commands
from discord.channel import DMChannel
from discord import Embed, TextChannel

from dirupl.address_directory.models import Guildinfo
from dirupl.address_directory.utils import Server_info_catcher, UserRegError, RustRegStatusError

from diruplbot.utils import ChangeChannelsMenuView

from diruplbot.utils import servers_to_msg, NoChannelsError

import logging

log = logging.getLogger("DiruplBot")


class ServerListenerCog(commands.Cog):
    
    def __init__(self, bot, rust_sockets):
        self.bot = bot
        self.rust_sockets=rust_sockets


    @commands.command(aliases=['LFS', 'lfs'], brief= 'Send to Direct `!LFS` to search server.', description='Looking for server command.')
    @commands.cooldown(1, 31, commands.BucketType.user)
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
            async with ctx.channel.typing():
                await sic.catch_info(term)
            await ctx.channel.send ('You can `!show` servers in Dirupl channel')  
        else:
            await ctx.channel.send ('You can search in Direct')

    @commands.command(aliases=['show', 'shows'], brief= 'Send to Direct `!show` to show your servers.')
    async def show_server(self, ctx):
        if isinstance(ctx.channel, DMChannel):
            await ctx.channel.send ('You can show servers in Dirupl channel')
            return
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id == int(guildinfo.channel_id):
            await servers_to_msg(ctx, self.rust_sockets)
        else:
            await ctx.channel.send ('You can show servers in Dirupl channel')

#################### Socket control #####################

    @commands.command(aliases=['start'], brief= '`!start` to receive messages from Rust plus.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def start_rust_socket(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can start in Dirupl channel')
            return
        if self.rust_sockets[ctx.guild.id]:
            await self.rust_sockets[ctx.guild.id].start()
        else:
            await ctx.channel.send ('Send `!show` to choose server')

    @commands.command(aliases=['stop'], brief= '`!stop` to stop rust notifications.')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stop_rust_socket(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can stop in Dirupl channel')
            return
        await self.rust_sockets[ctx.guild.id].break_socket()

#################### Show ##############################

    @commands.command(aliases=['show_time', 'st'], brief= 'Show server time.')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def show_server_time(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].check_server_time()

    @commands.command(aliases=['server', 'si', 'server_info', 'pop'], brief= 'Show server information.')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def show_server_info(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can show servir info in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].get_server_info()

    @commands.command(aliases=['shop'], brief= "Shows prices for an item in vending machines.")
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def show_vending_machine(self, ctx, item):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can show vending machines in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].get_vending_machines(item)

    @commands.command(aliases=['events'], brief= 'Show events')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def show_events(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can show events in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].get_server_events()

##################### Settings ##########################

    @commands.command(aliases=['cds'])
    async def change_distance_status(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can start in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].change_distance_status()

    @commands.command(aliases=['cls'])
    async def change_location_status(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can start in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].change_location_status()
    
##################### Other #############################

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: # check that message author is user
            return
        
        if message.guild is None: # check message guild
            return
        
        if not message.content or message.content.startswith("!"):
            return
        
        guildinfo = await Guildinfo.objects.filter(_guild_id=message.guild.id).afirst()
        if message.channel.id != int(guildinfo.channel_id):
            return
        
        rust_socket = self.rust_sockets[message.guild.id]
        if rust_socket.channel == message.channel:
            author = message.author
            await rust_socket.send_message(f'{author.name}: {message.content}')
            await message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = Embed(title=f"Slow it down bro!",description=f"Try again in {error.retry_after:.2f}s.")
            await ctx.send(embed=em, delete_after=error.retry_after)

    @commands.command(aliases=['test'], brief= 'test')
    async def try_test(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can start in Dirupl channel')
            return
        
        await self.rust_sockets[ctx.guild.id].check_time_loop()

    @commands.command(brief= 'Send to Direct `!change_channel` to choose another channel for Dirupl.')
    async def change_channel(self, ctx):
        guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
        if ctx.channel.id != int(guildinfo.channel_id):
            await ctx.channel.send ('You can show events in Dirupl channel')
            return
        
        try:
            channels = await self.collect_channels(ctx.guild.channels)
            await ctx.channel.send('', view = ChangeChannelsMenuView(guildinfo, channels))
        except NoChannelsError:
            await ctx.channel.send("I don't see chats that I can write to")

    async def collect_channels(self, all_channels):
        allowed_channels = []
        for channel in all_channels:
            if isinstance(channel, TextChannel):
                if channel.members:
                    allowed_channels.append(channel)
                    
        if allowed_channels:
            return allowed_channels
        raise NoChannelsError
    

