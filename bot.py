import asyncio
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import os

import django



load_dotenv()


intents = Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    help_command=commands.DefaultHelpCommand(),
    description='Dirupl',
    intents=intents,
    )

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\n')


def _setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dirupl.settings")
    django.setup()

async def main(TOKEN):
    
    async with bot:
        await bot.add_cog(DirectListenerCog(bot))
        await bot.start(TOKEN)
    

if __name__ == "__main__":
    _setup_django()
    
    from dirupl.settings import DISCORD_BOT_TOKEN
    from diruplbot.listeners import DirectListenerCog
    
    try:
        asyncio.run(main(DISCORD_BOT_TOKEN))
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Canceling tasks...")