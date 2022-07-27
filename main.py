from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter

lexer = Lexer("""
I said either false or false.
""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.GLOBAL_SCOPE)
