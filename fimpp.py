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
Dear Princess Celestia: Arrays!


Today I learned how to make arrays!

    (Without initialized values)
    Did you know that banana is the word "Banana Cake"?
    Did you know that carrot is the number 4? (Pointer - 4)

    Did you know that cake has many words?
    cake 1 is the word "Mango Cake". (Index 1)
    cake 2 is "Strawberry Cake". (Index 2)
    cake 3 is banana. (Index 3)
    cake`s carrot is "Carrot Cake". (Index 4)

    carrot got one less.

    I said cake`s carrot. (Index 3)

    (With initialized values)
    Did you know that Apples has words "Gala" and "Red Delicious" and "Mcintosh" and "Honeycrisp"?

    I said Apples 1.

That's all about how to make arrays.


Your faithful student, Vinyla Jaezmien Gael.""")

if __name__ == '__main__':
    interpret_from_command_line()
