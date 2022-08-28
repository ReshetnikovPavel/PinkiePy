import sys
import traceback
from colorama import Fore, Style
from pathlib import Path
import special_words

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


def interpret_file(absolute_path):
    if not absolute_path.is_file():
        print(f'{Fore.RED}File not found{Style.RESET_ALL}')
        return

    with absolute_path.open('r') as program_file:
        program = program_file.read()
        interpret(program)


def interpret_from_command_line():
    path = ' '.join(sys.argv[1:])
    interpret_file(Path(path).absolute())


if __name__ == '__main__':
    interpret_from_command_line()
