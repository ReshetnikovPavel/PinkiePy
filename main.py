from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter

lexer = Lexer("""

Did you know that a is true?
While a is true,
    I said a.
    a is now false.
That's what I did.
""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.environment)
