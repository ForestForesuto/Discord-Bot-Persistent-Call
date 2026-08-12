import discord
from discord.ext import commands
from src.helpers.central_logger import send_and_rotate_log

class LogSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="logs")
    async def send_logs(self, ctx: commands.Context):
        # Only allow in DM and only if the author is the owner
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("This command only works in DMs.")
            return
        
        if ctx.author.id != 921838663699161118:
            await ctx.send("You are not authorised.")
            return

        # Trigger the send function, will send the file and clear it
        await send_and_rotate_log()
        await ctx.send("Log file sent (if it existed) and cleared.")

async def setup(bot):
    await bot.add_cog(LogSender(bot))