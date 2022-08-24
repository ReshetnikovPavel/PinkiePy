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
Dear Princess Celestia: Recursion!

I learned how to do recursion using the number x!

    When x had more than 0.

        I said x!

        Did you know that y is the number x?
        y got one less.
        I remembered how to do recursion using y.

    That's what I would do.

That's all about how to do recursion.

Today I learned how to make recursion functions!

    Did you know that Twilight is the number 108?
    (Unfortunately it cannot handle bigger number)
    I remembered how to do recursion using Twilight.

That's all about how to make recursion functions.


Your faithful student, Twilight Sparkle.

""")


if __name__ == '__main__':
    interpret_from_command_line()
