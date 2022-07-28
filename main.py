from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter

lexer = Lexer("""

Did you know that a is "global"?
I said a.
If false:
    a becomes "local"?
    I said "a is " plus a.
That’s what I would do.
I said "a is " plus a.
""")
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
interpreter.interpret()
print(interpreter.environment)
