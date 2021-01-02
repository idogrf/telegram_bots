import sys
import subprocess
from telepot.helper import Sender

sys.path.append('/home/pi/projects/repositories/torrent_tools')
from torrent_tools.data_operations import delete_small_dirs, get_free_root_space, get_free_media_space
from torrent_tools.torrent_operations import refresh_rss_torrents, download_torrent, stop_all_torrents, start_all_torrents, list_torrents

from utils.handler import Handler


class TorrentHandler(Handler):
    """ Handles torrent related commands """
    def __init__(self, sender: Sender):
        super().__init__(sender)

        self.listening = False
        self._input_length = None
        self._input_params = []
        self._input_messages = []
        self._run_func = None

    @property
    def caller(self):
        return '/torrents'

    # Base class overloaded methods
    def run_command(self, msg_text, *args):
        if self.listening:
            self._input_param(msg_text)
            return

        self._process_command(msg_text)

    # Run command methods
    def _run_command_refresh(self):
        """ Refresh torrents RSS feed """
        self._sender.sendMessage('Refreshing torrents list.. please wait...')
        response = refresh_rss_torrents()
        self._sender.sendMessage('Finished refreshing torrents. Results - ')
        self._sender.sendMessage(response)

    def _run_command_download_torrent(self):
        """ Download new torrent """
        self.listening = True
        self._input_length = 2
        self._input_params = []
        self._input_messages = ['What should I download?', 'Where should I download to?']
        self._run_func = self._download_torrent

        self._sender.sendMessage(self._input_messages[-self._input_length])

    def _run_command_purge_dirs(self):
        """ Delete empty torrent folders """
        self._sender.sendMessage('Removing empty dirs')
        response = delete_small_dirs()
        self._sender.sendMessage(response)

    def _run_command_free_space(self):
        """ Check free disk space """
        media_space = get_free_media_space()
        root_space = get_free_root_space()
        self._sender.sendMessage(f'Free disk space on media mount - {media_space:.1f}GB')
        self._sender.sendMessage(f'Free disk space on root - {root_space:.1f}GB')

    def _run_command_start_all(self):
        """ Start all torrents """
        self._sender.sendMessage('Starting all torrents')
        response = start_all_torrents()
        self._sender.sendMessage(response)

    def _run_command_stop_all(self):
        """ Stop all active torrents """
        self._sender.sendMessage('Stopping all torrents')
        response = stop_all_torrents()
        self._sender.sendMessage(response)

    def _run_command_list(self):
        """ List all active torrents """
        response = list_torrents()
        self._sender.sendMessage(response)

    # Class helper methods
    def _download_torrent(self):
        self._sender.sendMessage(f'Downloading torrent')
        response = download_torrent(self._input_params[0], self._input_params[1])
        self._sender.sendMessage(response)

    def _input_param(self, msg):
        self._input_params.append(msg)
        self._input_length -= 1

        if self._input_length == 0:
            self._run_func()
            self.listening = False
            self._input_length = None
            self._input_params = []
            self._input_messages = []
            self._run_func = None
        else:
            self._sender.sendMessage(self._input_messages[-self._input_length])

