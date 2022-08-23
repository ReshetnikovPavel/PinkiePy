import sys
import special_words

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


interpret("""
Did you know that A likes many numbers?
A 0 is 0, A 1 is 42, A 2 is 69.
For every number c in A...
I said c.
That’s what I did.
""")

if __name__ == '__main__':
    interpret_from_command_line()
