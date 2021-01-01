import sys
import subprocess
from telepot.helper import Sender

sys.path.append('/home/pi/projects/cronjobs')
from download_torrents import run_torrent_download, delete_small_dirs, get_free_usb_space, get_free_root_space

from utils.handler import Handler


class TorrentHandler(Handler):
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

    @property
    def description(self):
        return f'Handles torrent related commands. type {self.caller} help for more information'

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
        output = run_torrent_download()
        self._sender.sendMessage('Finished refreshing torrents. Results - ')
        self._sender.sendMessage(output)

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
        deleted_dirs = delete_small_dirs()
        if len(deleted_dirs) == 0:
            self._sender.sendMessage('No dirs found for deletion')
        else:
            self._sender.sendMessage(f'Dirs deleted - {deleted_dirs}')

    def _run_command_free_space(self):
        """ Check free disk space """
        usb_space = get_free_usb_space()
        root_space = get_free_root_space()
        self._sender.sendMessage(f'Free disk space on USB - {usb_space:.1f}GB')
        self._sender.sendMessage(f'Free disk space on root - {root_space:.1f}GB')

    def _run_command_start_all(self):
        """ Start all torrents """
        self._sender.sendMessage('Starting all torrents')
        self._send_to_transmission(['--torrent', 'all', '--start'])

    def _run_command_stop_all(self):
        """ Stop all active torrents """
        self._sender.sendMessage('Stopping all torrents')
        self._send_to_transmission(['--torrent', 'all', '--stop'])

    # Class helper methods
    def _download_torrent(self):
        self._sender.sendMessage(f'Starting transmission torrent client')
        params = ['--add', self._input_params[0], '--download-dir', self._input_params[1]]
        self._send_to_transmission(params)

    def _send_to_transmission(self, params):
        p = subprocess.Popen(['transmission-remote', '--authenv'] + params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()

        output = output.decode("utf-8")
        err = err.decode("utf-8")

        print(output)
        print(err)

        if 'success' in output.lower() and len(err) == 0:
            self._sender.sendMessage(f'Success!')
            self._sender.sendMessage(f'You can check the progress by going to http://10.0.0.17:9091')
        else:
            self._sender.sendMessage(f'Failed')

        if len(output) > 0:
            self._sender.sendMessage(f'Output message - {output}')

        if len(err) > 0:
            self._sender.sendMessage(f'Output message - {err}')

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

