import time
import discord
import logging
from discord.ext import commands
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import MyBot

logger = logging.getLogger(__name__)

class SilenceAudioSource(discord.AudioSource):
    def __init__(self) -> None:
        self._counter = 0
        self._last_print_time = 0

    def read(self) -> bytes:
        try:
            self._counter += 1

            now = time.time()
            if self._counter % 10000 == 0 or (now - self._last_print_time) >= 30:
                logger.info(f"SilenceAudioSource: Still playing (call #{self._counter})")
                self._last_print_time = now
            # Return 20ms of silence PCM data, which is 3840 zero bytes
            # Never return b'' so it loops forever
            return bytes(3840)
        except Exception as e:
            # Log the error but keep the stream alive
            logger.error(f"SilenceAudioSource ERROR: {e}, Last print time: {self._last_print_time}")
            return bytes(3840)


    def is_opus(self) -> bool:
        # Return False to indicate we provide raw PCM data
        return False

    def cleanup(self) -> None:
        logger.info(f"SilenceAudioSource CLEANUP after {self._counter} calls")
        pass


class JoinVoiceCall(commands.Cog):
    def __init__(self, bot: MyBot) -> None:
        self.bot = bot

    @commands.command(name='join')
    @commands.guild_only()
    async def join(self, ctx: commands.Context) -> None:
        # Check if the user is in a voice channel
        logger.debug("Join Command Recieved")
        author = ctx.author
        if author.bot:
            return
        
        if not isinstance(author, discord.Member):
            await ctx.send("You're not a member?")
            return

        if not author.voice:
            await ctx.send("You are not in a voice channel, so I cannot join.")
            return

        # Get the user's voice channel
        channel = author.voice.channel
        if not channel:
            await ctx.send("You are not in a voice channel, so I cannot join.")
            return

        vc = ctx.voice_client

        # Check if the vc is a Voice Client
        if isinstance(vc, discord.VoiceClient):
            if vc.channel is None:
                await ctx.send("I'm in a weird state, please try again.")
                return

            # If the bot is already in the same channel, notify the user, otherwise move to the new channel
            if vc.channel == channel:
                await ctx.send(f"I'm already in `{channel.name}`.")
                return
            else:
                if vc.is_playing():
                    vc.stop()

                await vc.move_to(channel)
                await ctx.send(f"Moved to `{channel.name}`.")
                vc.play(SilenceAudioSource())
                return
        else:
            # Connect to the voice channel
            try:
                vc = await channel.connect()
            except Exception as e:
                logger.error(f"Error: {e}")
                await ctx.send(f"Something went wrong: {e}")
                return

            await ctx.send(f"Successfully joined the `{channel.name}` channel.")
            
            if vc.is_playing():
                vc.stop()

            vc.play(SilenceAudioSource())

    @commands.command(name='leave')
    @commands.guild_only()
    async def leave(self, ctx: commands.Context) -> None:
        logger.debug("Leave Command Recieved")
        author = ctx.author

        if author.bot:
            return
        
        if not isinstance(author, discord.Member):
            await ctx.send("You're not a member?")
            return

        vc = ctx.voice_client

        if isinstance(vc, discord.VoiceClient):
            await vc.disconnect()
            await ctx.send("Left the voice channel.")
        else:
            await ctx.send("I'm not in any voice channel.")


async def setup(bot: MyBot):
    await bot.add_cog(JoinVoiceCall(bot))