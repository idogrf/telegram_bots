import inspect
from telepot.helper import Sender


class Handler:
    def __init__(self, sender: Sender):
        self._sender = sender

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        relevant_methods = [method for method in methods if method[0].startswith('_run_command')]
        functions = [method[1] for method in relevant_methods]
        commands = [method[0].replace('_run_command_', '') for method in relevant_methods]
        docs = [function.__doc__ for function in functions]
        self._commands = [{'command': command, 'function': function, 'doc': doc}
                          for command, function, doc in zip(commands, functions, docs)]

    @property
    def caller(self):
        raise NotImplemented

    @property
    def description(self):
        raise NotImplemented

    def run_command(self, msg_text, *args):
        self._process_command(msg_text)

    def _process_command(self, in_command):
        in_command = in_command.replace(f'{self.caller}_', '').lstrip(' ')

        commands = [command for command in self._commands if command['command'] == in_command]
        command = commands[0] if len(commands)>0 else None
        if command is None:
            self._sender.sendMessage('Invalid command')
            self._run_command_help()
        else:
            command['function']()

    def _run_command_help(self):
        """ Get help for current handler """
        help_txt = f'usage: {self.caller}_<command> - \n'
        for command in self._commands:
            help_txt += f"   - {self.caller}_{command['command']} - {command['doc']}\n"
        self._sender.sendMessage(help_txt)
