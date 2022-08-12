from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """

Dear Princess Celestia: Math!

   I learned how to find maximum using first number and second number!
       Did you know that maximum was nothing?
       If first number is greater than second number, maximum becomes first number.
       Otherwise, maximum becomes second number.
       That's what I would do.
       Then you get maximum!
       
   That’s all about how to find maximum!
       
    I learned how to find minimum using first number and second number!
        Did you know that minimum was nothing?
        If first number is less than second number, minimum becomes first number.
        Otherwise, minimum becomes second number.
        That's what I would do.
        Then you get minimum!
        
    That’s all about how to find minimum!
   
   
Your faithful student, Kyli Rouge.

I said Math`s how to find minimum using 42 and 69!
I said Math`s how to find maximum using 42 and 69!

"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
