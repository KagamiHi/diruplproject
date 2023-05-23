from discord.ext import commands
from discord.channel import DMChannel

from dirupl.address_directory.utils import Server_info_catcher, UserRegError, RustRegStatusError


from diruplbot.utils import server_to_msg

from rustsocket.app import CustomRustSocket, PlayerIdTokenError

import logging

log = logging.getLogger("DiruplBot")


class ServerListenerCog(commands.Cog):
    
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