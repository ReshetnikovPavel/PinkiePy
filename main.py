from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter

lexer = Lexer("""
I wrote 8 and 7 plus 3 added to 19.
""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.GLOBAL_SCOPE)
