import sys

from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


def interpret(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    tree = parser.parse()
    resolver = Resolver(interpreter)
    resolver.resolve(tree)
    interpreter.interpret(tree)


def interpret_from_command_line():
    if len(sys.argv) != 2:
        print("Usage: fim++.py <filename>")
        sys.exit(1)
    program_file_name = sys.argv[1]
    if program_file_name.endswith('.fpp'):
        with open(program_file_name, 'r') as program_file:
            program = program_file.read()
            interpret(program)


if __name__ == '__main__':
    interpret_from_command_line()
