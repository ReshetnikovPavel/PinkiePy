from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """

Dear Princess Celestia: Class!

    Did you know that a is "Test"?
    
    I learned ab.
        Did you know that res is a?
        Then you get res plus "b".
    That's all about ab.
    

Your faithful student, Pavel Reshetnikov.

I said Class`s ab.

"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
