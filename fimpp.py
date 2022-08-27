import sys
import traceback
from contextlib import contextmanager

from colorama import Fore, Style

import fim_parser
import fim_resolver
import special_words
import utility

from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


def handle_errors(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except utility.FimException as e:
            print(f'{Fore.RED}{type(e).__name__}:'
                  f' {str(e)}{Style.RESET_ALL}')
        except KeyboardInterrupt:
            print(f'{Fore.RED}Program interrupted by user{Style.RESET_ALL}')
        except Exception as e:
            traceback.print_exc()
            print(f'{Fore.RED}Oops! There is some bug in interpreter!:'
                  f' {str(e)}{Style.RESET_ALL}')

    return wrapper


@handle_errors
def interpret(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    tree = parser.parse()
    resolver = Resolver(interpreter)
    resolver.resolve(tree)
    interpreter.interpret(tree)


def interpret_file(program_file_name):
    if program_file_name.endswith(special_words.extension):
        with open(program_file_name, 'r') as program_file:
            program = program_file.read()
            interpret(program)


def interpret_from_command_line():
    if len(sys.argv) != 2:
        print("Usage: fim++.py <filename>")
        sys.exit(1)
    interpret_file(sys.argv[1])


if __name__ == '__main__':
    interpret_from_command_line()
