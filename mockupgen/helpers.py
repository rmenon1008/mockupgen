from colorama import init as colorama_init
from colorama import Fore, Style
import argparse
import sys

colorama_init()

def _b(string):
    return f'{Fore.BLUE}{string}{Style.RESET_ALL}'

def _r(string):
    return f'{Fore.RED}{string}{Style.RESET_ALL}'

def _g(string):
    return f'{Fore.GREEN}{string}{Style.RESET_ALL}'

def _c(string):
    return f'{Fore.CYAN}{string}{Style.RESET_ALL}'

def _m(string):
    return f'{Fore.MAGENTA}{string}{Style.RESET_ALL}'

def _input_bool(prompt):
    while True:
        try:
            return {'y': True, 'n': False}[input(prompt).lower()]
        except KeyError:
            pass


class ColoredArgParser(argparse.ArgumentParser):

    def print_usage(self, file=None):
        if file is None:
            file = sys.stdout
        print(_b(self.format_usage()))

    def print_help(self, file=None):
        if file is None:
            file = sys.stdout
        print(self.format_help())

    def exit(self, status = 0, message = None):
        if message:
            print(_r(message), file=sys.stderr)
        sys.exit(status)

    def error(self, message):
        self.print_usage(sys.stderr)
        args = {'prog' : self.prog, 'message': message}
        self.exit(2, '%(prog)s: error: %(message)s\n' % args)