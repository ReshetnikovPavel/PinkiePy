import unittest
import sys
import io
from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter
from fim_resolver import Resolver


def interpret(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    tree = parser.parse()
    resolver = Resolver(interpreter)
    resolver.resolve(tree)
    interpreter.interpret(tree)


class Base(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def assert_printed(self, program, expected):
        self.old_stdout = sys.stdout  # Memorize the default stdout stream
        sys.stdout = self.buffer = io.StringIO()

        interpret(program)
        self.assertEqual(self.buffer.getvalue(), expected)

        sys.stdout = self.old_stdout


class TestOperators(Base):
    def test_addition(self):
        self.assert_printed('I said add 2 and 3.', '5\n')

    def testAddition2(self):
        self.assert_printed('Did you know that ten is 10? '
                            'Did you know that twelve is 2 plus ten?'
                            'I said twelve!', '12\n')

    def testAddition3(self):
        self.assert_printed('I wrote 8 and 7 plus 3 added to 19.', '37\n')

    def testIncrement(self):
        pass
        #   TODO: Implement increment operator

    def testSubtraction(self):
        self.assert_printed('I said subtract 5 and 7.', '-2\n')

    def testMultiplication(self):
        self.assert_printed('I said multiply 8 and 16!', '128\n')

    def testDivision(self):
        self.assert_printed('I said divide 8 and 2.', '4\n')

    def testDivision3(self):
        self.assert_printed('I wrote divide 2 by 9.', f'{2/9}\n')

    def testOutput(self):
        self.assert_printed('I said “Hello World”!', 'Hello World\n')

    def testOutput2(self):
        self.assert_printed('I wrote 99.', '99\n')

    def testOutput4(self):
        self.assert_printed('I said “Hello”! I said “World”.', 'Hello\nWorld\n')

    def testXor(self):
        self.assert_printed('I said either false or false.', 'false\n')
        self.assert_printed('I said either false or true.', 'true\n')
        self.assert_printed('I said either true or false.', 'true\n')
        self.assert_printed('I said either true or true.', 'false\n')


class TestPrograms(Base):
    def testMaximumMinimum(self):
        self.assert_printed("""
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
""",
                            '42\n69\n')


if __name__ == '__main__':
    unittest.main()
