import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import anthropic
import json
from collections import deque

# Import configuration
from config import (
    WATCH_MESSAGE_COUNT, AI_MODEL, MAX_TOKENS,
    BOT_PERSONALITY_FILE, BOT_MEMORY_FILE,
    BOT_TRIGGER, WELCOME_MESSAGE
)

# Load environment variables
load_dotenv()

# Get environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Validate environment variables
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in the environment")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set in the environment")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Load bot personality
def load_bot_personality():
    try:
        with open(BOT_PERSONALITY_FILE, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: {BOT_PERSONALITY_FILE} not found. Using default personality.")
        return "I am a friendly and helpful bot."

# Load bot memory
def load_bot_memory():
    try:
        with open(BOT_MEMORY_FILE, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Warning: {BOT_MEMORY_FILE} not found. Using default memory.")
        return "I don't have any specific memories yet."

bot_personality = load_bot_personality()
bot_memory = load_bot_memory()

# Initialize message queue and counter
message_queue = deque(maxlen=WATCH_MESSAGE_COUNT)
message_counter = 0

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=WELCOME_MESSAGE)

def handle_message(update, context):
    global message_counter

    user_message = update.message.text
    message_queue.append(user_message)
    message_counter += 1

    if message_counter >= WATCH_MESSAGE_COUNT:
        check_chime_in(context, update.effective_chat.id)
        message_counter = 0

    if BOT_TRIGGER in user_message.lower():
        respond_to_tag(update, context)

def check_chime_in(context, chat_id):
    messages = [
        {"role": "system", "content": bot_personality, "cache_control": {"type": "ephemeral"}},
        {"role": "system", "content": f"## Your memory: {bot_memory}", "cache_control": {"type": "ephemeral"}},
        {"role": "system", "content": "You are deciding whether to chime into a conversation. Respond with a JSON object with 'chime_in' (yes/no) and 'message' (your message or null)."},
        {"role": "user", "content": f"Recent messages: {list(message_queue)}"}
    ]

    response = client.messages.create(
        model=AI_MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages
    )

    try:
        decision = json.loads(response.content[0].text)
        if decision['chime_in'] == 'yes':
            context.bot.send_message(chat_id=chat_id, text=decision['message'])
    except json.JSONDecodeError:
        print("Error parsing API response")

def respond_to_tag(update, context):
    recent_messages = list(message_queue)

    messages = [
        {"role": "system", "content": bot_personality, "cache_control": {"type": "ephemeral"}},
        {"role": "system", "content": bot_memory, "cache_control": {"type": "ephemeral"}},
        {"role": "user", "content": f"Recent messages: {recent_messages}\nRespond to: {update.message.text}"}
    ]

    response = client.messages.create(
        model=AI_MODEL,
        max_tokens=MAX_TOKENS,
        messages=messages
    )

    context.bot.send_message(chat_id=update.effective_chat.id, text=response.content[0].text)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
