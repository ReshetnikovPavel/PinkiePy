from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver

lexer = Lexer("""

Dear Princess Celestia: Hello World!

    Today I learned how to say Hello World!
    I said “Hello World”!
    That’s all about how to say Hello World!

Your faithful student, Kyli Rouge.

Did you know that variable is Hello World?
I remembered variable`s how to say Hello World!

""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
print(interpreter.environment)
