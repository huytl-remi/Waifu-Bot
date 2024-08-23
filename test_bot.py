import unittest
from unittest.mock import patch, MagicMock
from collections import deque
import json

# Mock the entire anthropic module
anthropic_mock = MagicMock()
patch.dict('sys.modules', {'anthropic': anthropic_mock}).start()

# Now import from main
from main import start, handle_message, check_chime_in, respond_to_tag
from config import WELCOME_MESSAGE, BOT_TRIGGER, WATCH_MESSAGE_COUNT

class TestTelegramBot(unittest.TestCase):

    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()

        # Mock the bot personality and bot memory
        self.mock_bot_personality = "I am Waifu-chan, a friendly and enthusiastic bot!"
        self.mock_bot_memory = "This is Waifu-chan's memory content"

        patcher = patch.multiple('main',
            bot_personality=self.mock_bot_personality,
            bot_memory=self.mock_bot_memory,
            client=MagicMock()
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_start(self):
        start(self.update, self.context)
        self.context.bot.send_message.assert_called_once_with(
            chat_id=self.update.effective_chat.id,
            text=WELCOME_MESSAGE
        )

    @patch('main.message_queue', new_callable=lambda: deque(maxlen=WATCH_MESSAGE_COUNT))
    @patch('main.message_counter', new=0)
    @patch('main.check_chime_in')
    @patch('main.respond_to_tag')
    def test_handle_message(self, mock_respond_to_tag, mock_check_chime_in, mock_queue):
        self.update.message.text = "Test message"
        handle_message(self.update, self.context)
        self.assertEqual(len(mock_queue), 1)
        self.assertEqual(mock_queue[0], "Test message")

        # Test chime_in trigger
        for _ in range(WATCH_MESSAGE_COUNT - 1):
            handle_message(self.update, self.context)
        mock_check_chime_in.assert_called_once()

        # Test BOT_TRIGGER
        self.update.message.text = f"{BOT_TRIGGER} test"
        handle_message(self.update, self.context)
        mock_respond_to_tag.assert_called_once()

    @patch('main.client.messages.create')
    def test_check_chime_in(self, mock_create):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"chime_in": "yes", "message": "Hello there!"}')]
        mock_create.return_value = mock_response

        check_chime_in(self.context, 123)

        mock_create.assert_called_once()
        create_args = mock_create.call_args[1]
        self.assertEqual(create_args['messages'][0]['content'], self.mock_bot_personality)
        self.assertEqual(create_args['messages'][0]['cache_control'], {"type": "ephemeral"})
        self.assertIn(self.mock_bot_memory, create_args['messages'][1]['content'])
        self.assertEqual(create_args['messages'][1]['cache_control'], {"type": "ephemeral"})
        self.context.bot.send_message.assert_called_once_with(chat_id=123, text="Hello there!")

    @patch('main.client.messages.create')
    def test_respond_to_tag(self, mock_create):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Waifu-chan's response")]
        mock_create.return_value = mock_response

        self.update.message.text = f"{BOT_TRIGGER} test"
        respond_to_tag(self.update, self.context)

        mock_create.assert_called_once()
        create_args = mock_create.call_args[1]
        self.assertEqual(create_args['messages'][0]['content'], self.mock_bot_personality)
        self.assertEqual(create_args['messages'][0]['cache_control'], {"type": "ephemeral"})
        self.assertEqual(create_args['messages'][1]['content'], self.mock_bot_memory)
        self.assertEqual(create_args['messages'][1]['cache_control'], {"type": "ephemeral"})
        self.context.bot.send_message.assert_called_once_with(
            chat_id=self.update.effective_chat.id,
            text="Waifu-chan's response"
        )

if __name__ == '__main__':
    unittest.main()
