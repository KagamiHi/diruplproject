import asyncio
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import os

import django



load_dotenv()


intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    help_command=commands.DefaultHelpCommand(),
    description='Dirupl',
    intents=intents,
    )

rust_sockets = {}

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name}\n')


def _setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dirupl.settings")
    django.setup()

async def main(TOKEN):
    
    async with bot:
        await bot.add_cog(BaseListenerCog(bot, rust_sockets))
        await bot.add_cog(DirectListenerCog(bot))
        await bot.add_cog(ServerListenerCog(bot, rust_sockets))
        await bot.start(TOKEN)
    

if __name__ == "__main__":
    _setup_django()
    
    from dirupl.settings import DISCORD_BOT_TOKEN
    from diruplbot.listeners import BaseListenerCog, DirectListenerCog, ServerListenerCog

    try:
        asyncio.run(main(DISCORD_BOT_TOKEN))
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Canceling tasks...")