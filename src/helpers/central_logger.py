import sys
import io
import logging
import os
import asyncio
import discord

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

_bot = None
_owner_id = 921838663699161118

def set_bot(bot):
    global _bot
    _bot = bot

async def send_and_rotate_log():
    if _bot is None:
        return
    
    try:
        # Send the file
        user = await _bot.fetch_user(_owner_id)
        if user and os.path.exists("bot.log"):
            with open("bot.log", "rb") as f:
                file = discord.File(f, filename="bot.log")
                await user.send(content="Here are the logs:", file=file)

        # Close the handler, delete, reopen
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

                if os.path.exists("bot.log"):
                    os.remove("bot.log")

                # Reopen the file, the handler will reopen on next write
                handler.stream = open("bot.log", "a", encoding="utf-8")
                break

    except Exception as e:
        print(f"[LOG SEND ERROR] {e}")

# Logger setup
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.handlers.clear()

# Console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("bot.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Error‑triggered handler, sends log on ERROR
class ErrorHandler(logging.Handler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            asyncio.create_task(send_and_rotate_log())

error_handler = ErrorHandler()
error_handler.setLevel(logging.ERROR)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console.setFormatter(formatter)
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Add handlers
root_logger.addHandler(console)
root_logger.addHandler(file_handler)
root_logger.addHandler(error_handler)

logger = root_logger

# Background size checker
async def size_check_task():
    await asyncio.sleep(10)
    while True:
        if os.path.exists("bot.log"):
            size = os.path.getsize("bot.log")
            if size >= 8 * 1024 * 1024:
                await send_and_rotate_log()
        await asyncio.sleep(60)

# This will be started in bot.py after the bot is ready
def start_size_checker():
    asyncio.create_task(size_check_task())
