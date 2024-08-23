import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Anthropic API Key
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# You can add more configuration variables here as needed

# Validate that required environment variables are set
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in the environment")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment")
