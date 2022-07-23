import unittest
import sys
import io
from fim_lexer import Lexer
from fim_parser import Parser
from fim_interpreter import Interpreter


def interpret(program):
    lexer = Lexer(program)
    lexer.lex()
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    interpreter.interpret()


class Base(unittest.TestCase):
    def setUp(self):
        self.old_stdout = sys.stdout  # Memorize the default stdout stream
        sys.stdout = self.buffer = io.StringIO()

    def tearDown(self):
        sys.stdout = self.old_stdout

    def assert_printed(self, program, expected):
        interpret(program)
        self.assertEqual(self.buffer.getvalue(), expected)


class TestOperators(Base):
    def test_addition(self):
        self.assert_printed('I said add 2 and 3', '5\n')

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
        self.assert_printed('I said subtract 5 and 7', '-2\n')

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


if __name__ == '__main__':
    unittest.main()
