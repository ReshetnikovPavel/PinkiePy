from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter

lexer = Lexer("""

Did you know that I could is wrong?
Here’s what I did:
I said "a lot of things".
I did this as long as I could.

""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.environment)
