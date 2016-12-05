import sys
import os
import argparse
from smt import commands


class Driver:

    def __init__(self):
        self.__load_commands()

    def __load_commands(self):
        parser = argparse.ArgumentParser(description='Moderation Village Tool',
                                         add_help=True)
        subparsers = parser.add_subparsers()

        files = [c[:-3] for c in os.listdir(os.path.dirname(commands.__file__))
                 if c.endswith('.py') and not c.startswith('_')]

        for c in files:
            __import__(commands.__name__ + '.' + c)
            module = sys.modules[commands.__name__ + '.' + c]
            if hasattr(module, 'Command'):
                module.Command().register(
                    subparsers.add_parser(c, help=module.Command.help or c)
                )
        self._parser = parser

    def run(self, args):
        r = self._parser.parse_args(args[1:])
        r.handle(r)
