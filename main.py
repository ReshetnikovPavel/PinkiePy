from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


program = """
Dear Princess Celestia: Cider Jugs.

Today I learned Applejack's Drinking Song.
Did you know that Applejack likes 5? (Applejack likes a lot of things...)
I remembered how to sing the drinking song using Applejack.
That's all about Applejack's Drinking Song!

I learned how to sing the drinking song using ciders.
As long as ciders were more than 1.
I sang ciders" jugs of cider on the wall, "ciders" jugs of cider,".
There was one less ciders.
When ciders had more than 1, I sang "Take one down and pass it around, "ciders" jugs of cider on the wall."!
Otherwise, I sang "Take one down and pass it around, 1 jug of cider on the wall."!
That's what I would do, That's what I did.

I sang "1 jug of cider on the wall, 1 jug of cider.
Take it down and pass it around, no more jugs of cider on the wall.

No more jugs of cider on the wall, no more jugs of cider.
Go to the celler, get some more, 99 jugs of cider on the wall.".
That's all about how to sing the drinking song!

Your faithful student, Twilight Sparkle.

P.S. Twilight's drunken state truely frightened me, so I couldn't disregard her order to send you this letter. Who would have thought her first reaction to hard cider would be this... explosive? I need your advice, your help, everything, on how to deal with her drunk... self. -Spike
"""

lexer = Lexer(program)
lexer.lex()
parser = Parser(lexer)
interpreter = Interpreter(parser)
tree = parser.parse()
resolver = Resolver(interpreter)
resolver.resolve(tree)
interpreter.interpret(tree)
