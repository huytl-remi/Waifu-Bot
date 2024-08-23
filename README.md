# Waifu-chan Telegram Bot

This project implements a Telegram bot that uses the Anthropic API to generate responses. The bot, named Waifu-chan, can chime in on conversations and respond when tagged.

## Features

- Responds to direct messages when tagged with #waifu
- Chimes in on conversations periodically
- Uses Anthropic's API for generating responses
- Customizable bot personality and memory
- Easily configurable parameters

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with your Telegram Bot Token and Anthropic API Key:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
4. Customize the bot's personality in `memory/bot_personality.txt`
5. Add additional information to the bot's memory through `memory/bot_memory.txt`
6. Adjust bot configuration in `config.py` if needed
7. Run the bot: `python main.py`

## Configuration

You can adjust the following parameters in `config.py`:

- `WATCH_MESSAGE_COUNT`: Number of messages to watch before considering a chime-in
- `AI_MODEL`: AI model to use
- `MAX_TOKENS`: Maximum number of tokens for AI responses
- `BOT_PERSONALITY_FILE`: File path for the bot's personality
- `BOT_MEMORY_FILE`: File path for the bot's memory
- `BOT_TRIGGER`: Trigger word for direct interactions
- `WELCOME_MESSAGE`: Message sent when the bot starts

## Testing

Run the tests with: `python -m unittest test_bot.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This is a project of RENEC.
