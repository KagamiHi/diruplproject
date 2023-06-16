from discord.ext import commands
from discord.channel import DMChannel
from discord import Embed

from dirupl.address_directory.models import Guildinfo
from dirupl.address_directory.utils import Server_info_catcher, UserRegError, RustRegStatusError

from diruplbot.utils import ChangeChannelsMenuView, collect_channels

from diruplbot.utils import servers_to_msg, NoChannelsError

import logging

log = logging.getLogger("DiruplBot")


class ServerListenerCog(commands.Cog):
    
    def __init__(self, bot, rust_sockets):
        self.bot = bot
        self.rust_sockets=rust_sockets # dict of rust_sockets


    @commands.command(aliases=['LFS', 'lfs'], brief= 'Look for a server')
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

    @commands.command(aliases=['show', 'shows'], brief= 'Show senders servers')
    async def show_server(self, ctx):
        if ctx.guild.id in self.rust_sockets:
            rust_socket = self.rust_sockets[ctx.guild.id]
            channel_id = rust_socket.channel.id
        else:
            guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
            channel_id = int(guildinfo.channel_id)
        
        if ctx.channel.id == channel_id:
            await servers_to_msg(ctx, self.rust_sockets)
        else:
            await ctx.channel.send ('You can show servers in Dirupl channel')

    @commands.command(aliases=['dirupl'], brief= 'Show senders servers')
    async def show_dirupl_channel(self, ctx):
        if ctx.guild.id in self.rust_sockets:
            rust_socket = self.rust_sockets[ctx.guild.id]
            channel = rust_socket.channel.name
        else:
            guildinfo = await Guildinfo.objects.filter(_guild_id=ctx.guild.id).afirst()
            channel_id = int(guildinfo.channel_id)
            for c in ctx.guild.channels:
                if c.id == channel_id:
                    channel = c.name
                    break
        if not channel:
            return
        await ctx.channel.send (f'Dirupl channel: `{channel}`')


#################### Show ##############################

    @commands.command(aliases=['show_time', 'st'], brief= 'Show server time')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def show_server_time(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.get_server_time()

    @commands.command(aliases=['server', 'si', 'server_info', 'pop'], brief= 'Show server population')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def show_server_info(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.get_server_info()

    @commands.command(aliases=['shop'], brief= "Shows prices in vending machines")
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def show_vending_machines(self, ctx, item):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.get_vending_machines(item)

    @commands.command(aliases=['events'], brief= 'Show events')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def show_events(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.get_server_events()

##################### Settings ##########################

    @commands.command(aliases=['ceds'], brief= 'Show the distance to the event or not')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def change_event_distance_status(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.change_event_distance_status()

    @commands.command(aliases=['cels'], brief= 'Show the location of the event or not')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def change_event_location_status(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.change_event_location_status()
    
    @commands.command(aliases=['cvds'], brief= 'Show the distance to the vending machine or not')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def change_vend_distance_status(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.change_vend_distance_status()

    @commands.command(aliases=['cvls'], brief= 'Show the location of the vending machine or not')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def change_vend_location_status(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        await rust_socket.change_vend_location_status()

    @commands.command(aliases=['cc', 'changech'], brief= 'Choose another channel for Dirupl')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def change_channel(self, ctx):
        if not ctx.guild.id in self.rust_sockets:
            await ctx.channel.send ('Send `!show` to choose server')
            return
        
        rust_socket = self.rust_sockets[ctx.guild.id]
        if ctx.channel.id != rust_socket.channel.id:
            await ctx.channel.send ('You can show time in Dirupl channel')
            return
        
        try:
            channels = await collect_channels(self.bot, [c for c in ctx.guild.channels if c.id != ctx.channel.id])
            await ctx.channel.send('', view = ChangeChannelsMenuView(rust_socket, channels), delete_after=30)
        except NoChannelsError:
            await ctx.channel.send("I don't see chats that I can write to")

##################### Other #############################

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: # check that message author is user
            return
        
        if message.guild is None: # check message guild
            return
        
        if not message.content or message.content.startswith("!"):
            return
        
        if not message.guild.id in self.rust_sockets:
            return
        
        rust_socket = self.rust_sockets[message.guild.id]
        if message.channel.id != rust_socket.channel.id:
            return
        
        author = message.author
        await rust_socket.send_message(f'{author.name}: {message.content}')
        await message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            em = Embed(title=f"Slow it down bro!",description=f"Try again in {error.retry_after:.2f}s.")
            await ctx.send(embed=em, delete_after=error.retry_after)


    

