from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter

lexer = Lexer("""
Did you know that a is "before"?
I said a.
a is now "after".
I said a.

""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.GLOBAL_SCOPE)
