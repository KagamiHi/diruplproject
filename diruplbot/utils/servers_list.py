from dirupl.users.models import CustomUser
from dirupl.address_directory.models import Server
from .button import ServerButtonChooseView, ServerButtonDeclineView


async def server_to_msg(ctx):
    user = await CustomUser.objects.filter(discord_user_id=ctx.author.id).afirst()
    if user is None:
        await ctx.channel.send("You are not registered")
        return
    servers = Server.objects.filter(user=user)
    if servers is None:
        await ctx.channel.send("Send to Direct `!LFS` command")
        return
    
    async for server in servers:
        if server.stream:
            await ctx.channel.send(f'```• {server.name}\n{server.desc}```', view=ServerButtonDeclineView(server.id))
        else:
            await ctx.channel.send(f'```• {server.name}\n{server.desc}```', view=ServerButtonChooseView(server.id))
    return