from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """
I learned flail.
    I said "Flail!".
That's all about flail.

Did you know that Pinkie’s Tail is 4?

In regards to Pinkie’s Tail:
On the 1st hoof...
I said “That’s impossible!”.
On the 2nd hoof...
I said “There must be a scientific explanation”.
On the 3rd hoof...
I said “There must be an explanation”.
On the 4th hoof...
I said “Why does this happen?!”.
I would flail.
If all else fails...
I said “She’s just being Pinkie Pie.”.
That’s what I did.
"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
