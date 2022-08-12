from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """

Dear Princess Celestia: Linked List!

    Did you know that Next is nothing?
    Did you know that Value is nothing?
    
    I learned creation using next and value.
        Next becomes next.
        Value becomes value.
        Then you get this.
    That's all about creation.    

Your faithful student, Pavel Reshetnikov.

Did you know that node is Linked List`s creation using nothing and 1?
I said node`s Value.
node becomes Linked List`s creation using node and 2.
node becomes Linked List`s creation using node and 3.

I said node`s Value.
I said node`s Next`s Value.
I said node`s Next`s Next`s Value.



"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
