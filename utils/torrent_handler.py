import sys
import subprocess
from telepot.helper import Sender

sys.path.append('/home/pi/projects/cronjobs')
from download_torrents import run_torrent_download, delete_small_dirs


class TorrentHandler:
    def __init__(self, sender: Sender):
        self._sender = sender
        self.listening = False
        self._input_length = None
        self._input_params = []
        self._input_messages = []
        self._run_func = None

    def refresh_torrents(self):
        self._sender.sendMessage('Refreshing torrents list.. please wait...')
        output = run_torrent_download()
        self._sender.sendMessage('Finished refreshing torrents. Results - ')
        self._sender.sendMessage(output)

    def purge_dirs(self):
        self._sender.sendMessage('Removing empty dirs')
        deleted_dirs = delete_small_dirs()
        if len(deleted_dirs) == 0:
            self._sender.sendMessage('No dirs found for deletion')
        else:
            self._sender.sendMessage(f'Dirs deleted - {deleted_dirs}')

    def _run_download_torrent(self):
        self._sender.sendMessage(f'Starting transmission torrent client')
        params = ['--add', self._input_params[0], '--download-dir', self._input_params[1]]
        self._send_to_transmission(params)

    def _send_to_transmission(self, params):
        p = subprocess.Popen(['transmission-remote', '--authenv'] + params, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()

        print(output)
        print(err)

        if b'success' in output.lower() and len(err) == 0:
            self._sender.sendMessage(f'Success!')
            self._sender.sendMessage(f'Output message - {output}')
            self._sender.sendMessage(f'You can check the progress by going to http://10.0.0.17:9091')
        else:
            self._sender.sendMessage(f'Failed')
            self._sender.sendMessage(f'Error message - {output}')

    def input_param(self, msg):
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

    def download_torrent(self):
        self.listening = True
        self._input_length = 2
        self._input_params = []
        self._input_messages = ['What should I download?', 'Where should I download to?']
        self._run_func = self._run_download_torrent

        self._sender.sendMessage(self._input_messages[-self._input_length])

    def stop_all_torrents(self):
        self._sender.sendMessage('Stopping all torrents')
        self._send_to_transmission(['--torrent', 'all', '--stop'])




