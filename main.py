from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver

lexer = Lexer("""


I learned rec using x!
    
    I said "Here"!


That's all about rec.

Did you know that Twilight is 0?
    I said rec using Twilight.

""")
lexer.lex()
parser = Parser(lexer)
tree = parser.parse()
interpreter = Interpreter(parser)
resolver = Resolver(interpreter)
resolver.resolve_statements(tree.children)
interpreter.interpret(tree)
