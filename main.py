from lexer import Lexer
from fim_parser import Parser
from interpreter import Interpreter

lexer = Lexer("""
Did you know that number is 2?
Did you know that a is number?
Did you know that b is 10 times a plus 10 times number divided by 4?
Did you know that c is a plus b?
Did you know that x is 11?
""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.GLOBAL_SCOPE)
