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
Dear Princess Celestia: Fibonacci Sequence!

I learned how to find the fibonacci sequence to get a number using the number x!

    If x had no more than 1 then,
        Then you get x!
    That's what I would do.

    Did you know that ya is the number how to find the fibonacci sequence using x minus 1?
    Did you know that yb is the number how to find the fibonacci sequence using x minus 2?
    Then you get ya added to yb.

That's all about how to find the fibonacci sequence.


Today I learned how to run a program!

    Did you know that Twilight is the number 9?
    I said how to find the fibonacci sequence using Twilight. (Expected: 34)

That's all about how to run a program.


Your faithful student, Twilight Sparkle.

""")


if __name__ == '__main__':
    interpret_from_command_line()
