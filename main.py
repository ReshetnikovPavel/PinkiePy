from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """

Princess Luna:

I learned how to fly.
I learned how to do magic.
I learned how to raise the moon.

Your faithful student, Kyli Rouge.

Dear Princess Celestia and Princess Luna: Test!

Today I learned how to do many things!
    I remembered how to fly, I remembered how to do magic, I remembered how to raise the moon!
That's all about how to do many things.

I learned how to fly.
    I said "I can fly now".
That's all about how to fly.

I learned how to do magic.
    I said "Shazam"!
That's all about how to do magic.

I learned how to raise the moon.
    I said "cnreicofnouqefcnf".
That's all about how to raise the moon.

Your faithful student, Pavel Reshetnikov.

"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
