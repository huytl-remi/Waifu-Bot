# Telegram Bot with Anthropic API

This project implements a Telegram bot that uses the Anthropic API to generate responses. The bot can chime in on conversations and respond when tagged.

## Features

- Responds to direct messages
- Chimes in on conversations periodically
- Uses Anthropic's API for generating responses
- Customizable bot personality
- Caching mechanism for improved performance

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your `.env` file with your Telegram Bot Token and Anthropic API Key
4. Customize the bot's personality in `memory/bot_personality.txt`
5. Run the bot: `python main.py`

## Testing

Run the tests with: `python -m unittest test_bot.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This is a project of RENEC.
