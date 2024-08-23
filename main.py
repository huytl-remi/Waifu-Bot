import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import anthropic
import json
from collections import deque
from config import TELEGRAM_TOKEN, ANTHROPIC_API_KEY
from cached_content import get_cached_content

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Load bot personality and cached content
with open('./memory/bot_personality.txt', 'r') as file:
    bot_personality = file.read()

cached_content = get_cached_content()

# Initialize message queue and counter
message_queue = deque(maxlen=20)
message_counter = 0

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello! I'm your friendly chat bot. How can I help you today?")

def handle_message(update, context):
    global message_counter

    user_message = update.message.text
    message_queue.append(user_message)
    message_counter += 1

    if message_counter >= 20:
        check_chime_in(context, update.effective_chat.id)
        message_counter = 0

    if '#chatbuddy' in user_message.lower():
        respond_to_tag(update, context)

def check_chime_in(context, chat_id):
    messages = [
        {"role": "system", "content": "You are deciding whether to chime into a conversation. Respond with a JSON object with 'chime_in' (yes/no) and 'message' (your message or null)."},
        {"role": "user", "content": f"Recent messages: {list(message_queue)}"}
    ]

    response = client.messages.create(
        model="claude-3-sonnet-20240320",
        max_tokens=1024,
        system=bot_personality,
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
        {"role": "system", "content": bot_personality},
        {"role": "system", "content": cached_content, "cache_control": {"type": "ephemeral"}},
        {"role": "user", "content": f"Recent messages: {recent_messages}\nRespond to: {update.message.text}"}
    ]

    response = client.messages.create(
        model="claude-3-sonnet-20240320",
        max_tokens=1024,
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
