from dirupl.users.models import CustomUser
from dirupl.address_directory.models import Server
from .servers_menu import ServersMenuView


async def servers_to_msg(ctx, rust_sockets):
    user = await CustomUser.objects.filter(discord_user_id=ctx.author.id).afirst()
    if user is None:
        await ctx.channel.send("You are not registered")
        return
    servers = Server.objects.filter(user=user)
    if servers is None:
        await ctx.channel.send("Send to Direct `!LFS` command")
        return
    
    servers_list = [server async for server in servers]
    await ctx.channel.send(f"{ctx.author.display_name}'s servers list:", view=ServersMenuView(rust_sockets, servers_list))
    return