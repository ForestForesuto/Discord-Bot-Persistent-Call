"""Load and export environment variables from .env."""

import os
from dotenv import load_dotenv

from src.helpers.path_finder import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")
BOT_TOKEN = os.environ["TOKEN"]