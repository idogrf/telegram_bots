import os
import json
from telepot.helper import Sender

from utils.utils import generate_pass
from utils.email_handler import EmailHandler


class Verifier:
    def __init__(self, sender: Sender, email: str, password: str):
        self._sender = sender
        self._verifying = False
        self._random_pass = None
        self._email_handler = EmailHandler(email, password)

    @property
    def verifying(self):
        return self._verifying

    @staticmethod
    def _get_verified_chats():
        if os.path.exists('verified_chat_ids.txt'):
            with open('verified_chat_ids.txt', 'r') as f:
                verified = json.load(f)
            return verified['chat_ids']
        else:
            return []

    def verify_chat_id(self, chat_id):
        chat_id_verified = chat_id in Verifier._get_verified_chats()
        return chat_id_verified

    def generate_password(self):
        self._random_pass = generate_pass(8)
        self._verifying = True
        print(self._random_pass)
        self._email_handler.send_password(self._random_pass)
        self._sender.sendMessage('Please provide matching password (sent to email)')

    def purge_chat_ids(self):
        self._save_verified_chat_ids([])
        self._sender.sendMessage('Accounts permissions purged')

    @staticmethod
    def _save_verified_chat_ids(verified_chat_ids):
        with open('verified_chat_ids.txt', 'w') as f:
            json.dump({'chat_ids': verified_chat_ids}, f)

    def register_chat_id(self, msg_text, chat_id):
        if msg_text == self._random_pass:
            self._verifying = False
            self._random_pass = None

            verified_chat_ids = Verifier._get_verified_chats() + [chat_id]
            self._save_verified_chat_ids(verified_chat_ids)

            self._sender.sendMessage('Chat ID registered successfully!')
        else:
            self._verifying = False
            self._random_pass = None
            self._sender.sendMessage('Password incorrect! Please try again!')
