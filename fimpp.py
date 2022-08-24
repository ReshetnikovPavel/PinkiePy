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
Dear Princess Celestia: Digital Root!


I learned how to find the digital root to get a number using a number x!

    Did you know that y is the number 0?
    Did you know that z is the word convert a number to literal string using x.

    For every character v in z...
        Did you know that w is the number convert a char to literal num using v?
        w became y plus w.
        w became w minus 1.
        w became w mod 9.
        w became 1 plus w.
        y became w.
    That's what I did.
    
    Then you get y!

That's all about how to find the digital root.

Today I learned how to run a program!

    I said how to find the digital root using 34758. (Expected: 9)

That's all about how to run a program.


Your faithful student, Jaezmien Naejara.
P.S. https://esolangs.org/wiki/Digital_root_calculator""")


if __name__ == '__main__':
    interpret_from_command_line()
