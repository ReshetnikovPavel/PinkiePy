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
Dear Princess Celestia: For loops!


Today I learned how to do a for loop!

    Did you know that Applejack is the word "Apples"?

    For every number index from 0 to 100...
        I said index.
    That's what I did.

    For every character c in Applejack...
        I said c.
    That's what I did.

    Did you know that Apples has the words "Gala" and "Red Delicious" and "Mcintosh" and "Honeycrisp"?

    For every word type in Apples...
        I said type.
    That's what I did.

That's all about how to do a for loop.


Your faithful student, Twilight Sparkle.
""")


if __name__ == '__main__':
    interpret_from_command_line()
