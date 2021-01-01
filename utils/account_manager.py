import os
import json
from telepot.helper import Sender

from utils.utils import generate_pass
from utils.email_handler import EmailHandler


class AccountManager:
    def __init__(self, sender: Sender, email: str, password: str, verified_chats_file: str):
        self._sender = sender
        self.listening = False
        self._random_pass = None
        self._email_handler = EmailHandler(email, password)
        self._verified_chats_file = verified_chats_file

    def run_command(self, msg_text, chat_id):

        if self.listening:
            self._register_chat_id(msg_text, chat_id)
            return

        command = msg_text.lstrip('/acm').lstrip(' ')

        if command == 'help':
            self._get_help()
        elif command == 'purge':
            self._purge_chat_ids()
        else:
            self._sender.sendMessage('Invalid command')
            self._get_help()

    def _get_help(self):
        help_txt = 'Account Manager module available commands - \n'
        help_txt += '   - register - Register new account\n'
        help_txt += '   - purge - Delete all accounts permission\n'
        self._sender.sendMessage(help_txt)

    def _get_verified_chats(self):
        if os.path.exists(self._verified_chats_file):
            with open(self._verified_chats_file, 'r') as f:
                verified = json.load(f)
            return verified['chat_ids']
        else:
            return []

    def verify_chat_id(self, chat_id):
        chat_id_verified = chat_id in self._get_verified_chats()
        return chat_id_verified

    def generate_password(self, chat_id):
        if not self.verify_chat_id(chat_id):
            self._random_pass = generate_pass(16)
            self.listening = True
            print(self._random_pass)
            self._email_handler.send_password(self._random_pass)
            self._sender.sendMessage('Please provide matching password (sent to email)')
        else:
            self._sender.sendMessage('Account already registered')

    def _purge_chat_ids(self):
        self._save_verified_chat_ids([])
        self._sender.sendMessage('Accounts permissions purged')

    def _save_verified_chat_ids(self, verified_chat_ids):
        if not os.path.exists(os.path.dirname(self._verified_chats_file)):
            os.makedirs(os.path.dirname(self._verified_chats_file))
        with open(self._verified_chats_file, 'w') as f:
            json.dump({'chat_ids': verified_chat_ids}, f)

    def _register_chat_id(self, msg_text, chat_id):
        if msg_text == self._random_pass:
            self.listening = False
            self._random_pass = None

            verified_chat_ids = self._get_verified_chats() + [chat_id]
            self._save_verified_chat_ids(verified_chat_ids)

            self._sender.sendMessage('Chat ID registered successfully!')
        else:
            self.listening = False
            self._random_pass = None
            self._sender.sendMessage('Password incorrect! Please try again!')
