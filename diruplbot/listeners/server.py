from discord.ext import commands
from discord.channel import DMChannel

from dirupl.address_directory.models import Guildinfo
from dirupl.address_directory.utils import Server_info_catcher, UserRegError, RustRegStatusError


from diruplbot.utils import servers_to_msg, Guild

from rustsocket.app import CustomRustSocket, PlayerIdTokenError

import logging

log = logging.getLogger("DiruplBot")


class ServerListenerCog(commands.Cog):
    
    def __init__(self, bot, rust_sockets):
        self.bot = bot
        self.rust_sockets=rust_sockets

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
            async with ctx.channel.typing():
                await sic.catch_info(term)
            await ctx.channel.send ('You can ```!show``` servers in Dirupl channel')  
        else:
            await ctx.channel.send ('You can search in Direct')

    @commands.command(aliases=['show', 'shows'], brief= 'Send to Direct `!show` to show your servers.')
    async def show_server(self, ctx):
        guildinfo = await Guildinfo.objects.filter(guild_id=ctx.guild.id).afirst()
        if ctx.channel.id == int(guildinfo.channel_id):
            await servers_to_msg(ctx, self.rust_sockets)
        else:
            await ctx.channel.send ('You can show in Dirupl channel')

    @commands.command(aliases=['start'], brief= '`!start` to receive messages from Rust plus.')
    async def start_stream(self, ctx):
        await self.rust_sockets[ctx.guild.id].start()

    @commands.command(aliases=['stop'], brief= '`!stop` to stop rust notifications.')
    async def stop_rust_socket(self, ctx):
        await self.rust_sockets[ctx.guild.id].break_socket()

    @commands.command(aliases=['test'], brief= 'test')
    async def try_test(self, ctx):
        await self.rust_sockets[ctx.guild.id].change_time_status()

    @commands.command(aliases=['show_time'], brief= 'Show server time.')
    async def show_server_time(self, ctx):
        await self.rust_sockets[ctx.guild.id].check_server_time()

    @commands.command(aliases=['server'], brief= 'Show server information.')
    async def show_server_info(self, ctx):
        await self.rust_sockets[ctx.guild.id].take_server_info()