from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver

lexer = Lexer("""


I learned rec using x!
    
    x got one more.
    If x is less than 90 then:
        x is now rec using x!
    That‘s what I would do.
    Then you get x!


That's all about rec.

Did you know that Twilight is 0?
    I said rec using Twilight.

""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
print(interpreter.environment)
