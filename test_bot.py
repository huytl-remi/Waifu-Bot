import unittest
from unittest.mock import patch, MagicMock
from collections import deque
import json

# Mock the entire anthropic module
anthropic_mock = MagicMock()
patch.dict('sys.modules', {'anthropic': anthropic_mock}).start()

# Now import from main
from main import start, handle_message, check_chime_in, respond_to_tag

class TestTelegramBot(unittest.TestCase):

    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()

        # Mock the bot personality and cached content
        self.mock_bot_personality = "I am a friendly bot"
        self.mock_cached_content = "This is cached content"

        patcher = patch.multiple('main',
            bot_personality=self.mock_bot_personality,
            cached_content=self.mock_cached_content,
            client=MagicMock()
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_start(self):
        start(self.update, self.context)
        self.context.bot.send_message.assert_called_once_with(
            chat_id=self.update.effective_chat.id,
            text="Hello! I'm your friendly chat bot. How can I help you today?"
        )

    @patch('main.message_queue', new_callable=lambda: deque(maxlen=20))
    @patch('main.message_counter', new=0)
    @patch('main.check_chime_in')
    @patch('main.respond_to_tag')
    def test_handle_message(self, mock_respond_to_tag, mock_check_chime_in, mock_queue):
        self.update.message.text = "Test message"
        handle_message(self.update, self.context)
        self.assertEqual(len(mock_queue), 1)
        self.assertEqual(mock_queue[0], "Test message")

        # Test chime_in trigger
        for _ in range(19):
            handle_message(self.update, self.context)
        mock_check_chime_in.assert_called_once()

        # Test #chatbuddy trigger
        self.update.message.text = "#chatbuddy test"
        handle_message(self.update, self.context)
        mock_respond_to_tag.assert_called_once()

    @patch('main.client.messages.create')
    def test_check_chime_in(self, mock_create):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text='{"chime_in": "yes", "message": "Hello there!"}')]
        mock_create.return_value = mock_response

        check_chime_in(self.context, 123)

        self.context.bot.send_message.assert_called_once_with(chat_id=123, text="Hello there!")

    @patch('main.client.messages.create')
    def test_respond_to_tag(self, mock_create):
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Bot response")]
        mock_create.return_value = mock_response

        self.update.message.text = "#chatbuddy test"
        respond_to_tag(self.update, self.context)

        self.context.bot.send_message.assert_called_once_with(
            chat_id=self.update.effective_chat.id,
            text="Bot response"
        )

if __name__ == '__main__':
    unittest.main()
