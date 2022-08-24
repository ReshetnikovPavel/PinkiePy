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
Dear Princess Celestia: Fizzbuzz!


Today I learned how to play fizzbuzz!

    Did you know that Applebloom is the number 1?

    As long as Applebloom had no more than 100,

        Did you know that Babs Seed is the word ""? (Store the result!)

        If Applebloom modulo 3 is 0 then, (...Is Applebloom divisible by 3?)
            Babs Seed became Babs Seed plus "Fizz".
        That's what I would do.
        If Applebloom modulo 5 is 0 then, (... Is Applebloom divisible by 5?)
            Babs Seed became Babs Seed plus "Buzz".
        That's what I would do.

        (Now we check if result is still empty, which means it's not divisible by 3 or 5!)
        If Babs Seed is the word nothing then,
            Babs Seed became Applebloom. (String conversion!)
        That's what I would do.

        I said Applebloom " - " Babs Seed.
        Applebloom got one more.

    That's what I did.
    
That's all about how to play fizzbuzz.


Your faithful student, Jaezmien Naejara.
""")


if __name__ == '__main__':
    interpret_from_command_line()
