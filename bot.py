import asyncio
import discord
import random
import logging
from discord.ext import commands, tasks
from src.helpers.env_helper import BOT_TOKEN
from keep_alive import keep_alive
from src.helpers.central_logger import set_bot, start_size_checker

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

class MyBot(commands.Bot):
    async def setup_bot(self):
        extensions = [
            "src.voice_join.voice_call_manager",
            "src.voice_join.detector",
            "src.voice_join.log_sender"
        ]

        for ext in extensions:
            await self.load_extension(ext)


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.reactions = True
intents.members = True
intents.voice_states = True

bot = MyBot(command_prefix="v!", intents=intents)

@tasks.loop(minutes=3)
async def rotate_presence():
    websocket = getattr(bot, "ws", None)
    if websocket is None or not websocket.open:
        return

    presences = [
        discord.Activity(type=discord.ActivityType.watching, name=f"Looking at Voice Calls"),
        discord.Activity(
            type=discord.ActivityType.playing,
            name=f"Hearing {sum(guild.member_count or 0 for guild in bot.guilds)} People",
        ),
    ]

    if not bot.is_closed():
        await bot.change_presence(activity=random.choice(presences))


@rotate_presence.before_loop
async def before_rotate():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    if not rotate_presence.is_running():
        rotate_presence.start()

    set_bot(bot)
    start_size_checker()
    logger.info(f"Logged in as {bot.user}")


async def main():
    keep_alive()
    async with bot:
        await bot.setup_bot()
        await bot.start(BOT_TOKEN)


asyncio.run(main())