import os
import sys
import time

import telepot
from telepot.loop import MessageLoop
from telepot.delegate import pave_event_space, per_chat_id, create_open

from utils.account_manager import AccountManager
from utils.torrent_handler import TorrentHandler

sys.path.append('/home/pi/projects/cronjobs')
from download_torrents import run_torrent_download, delete_small_dirs


class CommandParser(telepot.helper.ChatHandler):
	def __init__(self, *args, **kwargs):
		email = kwargs.pop('email')
		password = kwargs.pop('password')

		super(CommandParser, self).__init__(*args, **kwargs)
		self._account_manager = AccountManager(self.sender, email, password)
		self._torrent_handler = TorrentHandler(self.sender)

	def on__idle(self, event):
		if self._account_manager.listening:
			self.sender.sendMessage('Time expired. please try again')
		self.close()

	def on_chat_message(self, msg):
		content_type, chat_type, chat_id = telepot.glance(msg)
		if content_type != 'text':
			self.sender.sendMessage(f"Sorry, I can only understand text")
			return

		msg_text = msg['text']
		print(f'Received msg - {msg_text}')
		print(self.chat_id)

		chat_id_verified = self._account_manager.verify_chat_id(self.chat_id)

		if msg_text == '/help':
			self.sender.sendMessage(f"I can't help yet =/")

		elif msg_text == '/status':
			if chat_id_verified:
				self.sender.sendMessage('User is registered. Can use all commands')
			else:
				self._sender.sendMessage('User is not registered. Please register account using /acm register')

		elif msg_text == '/acm register':
			self._account_manager.generate_password(self.chat_id)

		elif self._account_manager.listening:
			self._account_manager.run_command(msg_text, self.chat_id)

		elif not chat_id_verified:
			self._sender.sendMessage('Permission denied. Please register account using /acm register')
			return

		elif msg_text.startswith('/acm'):
			self._account_manager.run_command(msg_text, self.chat_id)

		elif msg_text.startswith('/torrents') or self._torrent_handler.listening:
			self._torrent_handler.run_command(msg_text)

		elif msg_text.lower().startswith(('hi', 'hello', 'hey')):
			self.sender.sendMessage(f"Hi there! I'm PI bot :) how can I help?")

		else:
			self.sender.sendMessage(f"Sorry, I don't understand... please type /help for further options")


def run():
	email = os.getenv('EMAIL_ADD')
	password = os.getenv('EMAIL_PASS')
	bot_token = os.getenv('TEL_BOT_TOKEN')

	bot = telepot.DelegatorBot(bot_token, [pave_event_space()(per_chat_id(),
															  create_open,
															  CommandParser,
															  timeout=30,
															  email=email,
															  password=password)])
	MessageLoop(bot).run_as_thread()
	print('Listening...')

	while 1:
		time.sleep(10)

if __name__ == '__main__':
	run()
