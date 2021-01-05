import os
import json
from telepot.helper import Sender

from utils.handler import Handler
from utils.utils import generate_pass
from utils.email_utils import EmailHandler


class AccountHandler(Handler):
    """ Handles account related commands """

    def __init__(self, sender: Sender, email: str, password: str, verified_chats_file: str, msg_info):
        super().__init__(sender)

        self.register_func_caller = '/acm_register'
        self.listening = False
        self._random_pass = None
        self._email_handler = EmailHandler(email, password, msg_info)
        self._verified_chats_file = verified_chats_file

    @property
    def caller(self):
        return '/acm'

    # Base class overloaded methods
    def run_command(self, msg_text, chat_id=None, *args):

        if self.listening:
            self._register_account(msg_text, chat_id)
            return

        self._process_command(in_command=msg_text)

    # Run command methods
    def _run_command_purge(self):
        """ Purge all user accounts """
        self._save_verified_chat_ids([])
        self._sender.sendMessage('Accounts permissions purged')

    # Class helper methods
    def _register_account(self, msg_text, chat_id):
        """ Register user account for elevated permissions """
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
            self._random_pass = generate_pass(6)
            self.listening = True
            print(self._random_pass)
            self._email_handler.send_password(self._random_pass)
            self._sender.sendMessage('Please provide matching password (sent to email)')
        else:
            self._sender.sendMessage('Account already registered')

    def _save_verified_chat_ids(self, verified_chat_ids):
        if not os.path.exists(os.path.dirname(self._verified_chats_file)):
            os.makedirs(os.path.dirname(self._verified_chats_file))
        with open(self._verified_chats_file, 'w') as f:
            json.dump({'chat_ids': verified_chat_ids}, f)
