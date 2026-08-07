import discord
import logging
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import MyBot

logger = logging.getLogger(__name__)

class Listener(commands.Cog):
    def __init__(self, bot: MyBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if self.bot.user is None:
            return
        
        if before.channel != after.channel:
            logger.debug(f"Voice state change: {member.name} {before.channel} -> {after.channel}")

        if member.id != self.bot.user.id:
            return

        # Bot disconnected
        if before.channel is not None and after.channel is None:
            logger.info(f"⚠️ Bot was disconnected from {before.channel.name} (ID: {before.channel.id})")
        # Bot connected
        elif before.channel is None and after.channel is not None:
            logger.info(f"✅ Bot joined {after.channel.name} (ID: {after.channel.id})")
        # Bot moved
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            logger.info(f"🔄 Bot moved from {before.channel.name} to {after.channel.name}")


async def setup(bot: MyBot):
    await bot.add_cog(Listener(bot))