import os
import json

import telepot


class UpdaterBot:
    def __init__(self, bot=None):
        bot_token = os.getenv('TEL_BOT_TOKEN')
        subscribed_chats_file = os.getenv('SUBSCRIBED_CHATS_FILE')
        with open(subscribed_chats_file, 'r') as f:
            subscribed_chats = json.load(f)

        self._subscribed_chat_ids = subscribed_chats['chat_ids']
        self._bot = bot if bot is not None else telepot.Bot(bot_token)

    def update_subscribers(self, msg):
        for chat_id in self._subscribed_chat_ids:
            self._bot.sendMessage(chat_id, msg)
