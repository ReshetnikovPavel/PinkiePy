from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """

Dear Princess Celestia: A!

    Did you know that field is 1?

Your faithful student, Pavel Reshetnikov.

Dear A: B!

    I learned how to find super's field!
        I said field!
    That's all about how to find super's field.

Your faithful student, Pavel Reshetnikov.

I remembered B`s how to find super's field.


"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
