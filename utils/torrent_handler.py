import sys
import subprocess
from telepot.helper import Sender

sys.path.append('/home/pi/projects/cronjobs')
from download_torrents import run_torrent_download, delete_small_dirs, get_free_usb_space, get_free_root_space


class TorrentHandler:
    def __init__(self, sender: Sender):
        self._sender = sender
        self.listening = False
        self._input_length = None
        self._input_params = []
        self._input_messages = []
        self._run_func = None

    def run_command(self, msg_text):

        if self.listening:
            self._input_param(msg_text)
            return

        command = msg_text.lstrip('/torrents').lstrip(' ')

        if command == 'help':
            self._get_help()
        elif command == 'refresh':
            self._refresh_torrents()
        elif command == 'purge':
            self._purge_dirs()
        elif command == 'download':
            self._download_torrent()
        elif command == 'stop all':
            self._stop_all_torrents()
        elif command == 'free space':
            self._check_free_space()
        else:
            self._sender.sendMessage('Invalid command')
            self._get_help()

    def _get_help(self):
        help_txt = 'Torrents module available commands - \n'
        help_txt += '   - refresh - Refresh torrents RSS feed\n'
        help_txt += '   - download - Download new torrent\n'
        help_txt += '   - purge - Delete empty torrent folders\n'
        help_txt += '   - stop all - Stop all active torrents\n'
        help_txt += '   - free space - Get free space on device\n'
        self._sender.sendMessage(help_txt)


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

    def _refresh_torrents(self):
        self._sender.sendMessage('Refreshing torrents list.. please wait...')
        output = run_torrent_download()
        self._sender.sendMessage('Finished refreshing torrents. Results - ')
        self._sender.sendMessage(output)

    def _purge_dirs(self):
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

    def _download_torrent(self):
        self.listening = True
        self._input_length = 2
        self._input_params = []
        self._input_messages = ['What should I download?', 'Where should I download to?']
        self._run_func = self._run_download_torrent

        self._sender.sendMessage(self._input_messages[-self._input_length])

    def _stop_all_torrents(self):
        self._sender.sendMessage('Stopping all torrents')
        self._send_to_transmission(['--torrent', 'all', '--stop'])

    def _check_free_space(self):
        usb_space = get_free_usb_space()
        root_space = get_free_root_space()
        self._sender.sendMessage(f'Free disk space on USB - {usb_space:.1f}GB')
        self._sender.sendMessage(f'Free disk space on root - {root_space:.1f}GB')



