import sys
import traceback
import argparse

from colorama import Fore, Style
from pathlib import Path

from fim_debugger import Debugger
from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver
from fim_exception import FimException


def handle_errors(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except FimException as e:
            print(f'{Fore.RED}{type(e).__name__}:'
                  f' {str(e)}{Style.RESET_ALL}')
        except KeyboardInterrupt:
            print(f'{Fore.RED}Program interrupted by user{Style.RESET_ALL}')
        except RecursionError:
            print(f'{Fore.RED}Recursion error{Style.RESET_ALL}')
        except Exception as e:
            traceback.print_exc()
            print(f'{Fore.RED}Oops! There is some bug in the interpreter!:'
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


@handle_errors
def interpret_by_line(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Debugger(parser, program)
    tree = parser.parse()
    resolver = Resolver(interpreter)
    resolver.resolve(tree)
    interpreter.interpret(tree)


def interpret_file(absolute_path, interpret_function=interpret):
    if not absolute_path.is_file():
        print(f'{Fore.RED}File not found{Style.RESET_ALL}')
        return

    with absolute_path.open('r') as program_file:
        program = program_file.read()
        interpret_function(program)


def interpret_from_command_line():
    args = parse_args()
    path = args.path
    line_by_line = args.line_by_line
    if line_by_line:
        interpret_file(Path(path).absolute(), interpret_by_line)
    else:
        interpret_file(Path(path).absolute())


def parse_args():
    parser = argparse.ArgumentParser()
    add_args(parser)
    return parser.parse_args()


def add_args(parser):
    parser.add_argument('path', type=str, help='Path to file')
    parser.add_argument('-l', '--line-by-line',
                        action='store_true',
                        help='Run interpreter line by line')


if __name__ == '__main__':
    interpret_from_command_line()
